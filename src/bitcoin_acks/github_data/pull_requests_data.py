import json
import os
import re
from datetime import datetime

import postgres_copy
import pytz
from dateutil.parser import parse
from sqlalchemy.exc import NoResultFound

from bitcoin_acks.constants import PullRequestState, ReviewDecision
from bitcoin_acks.data_schemas import pull_request_schema
from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.comments_data import CommentsData
from bitcoin_acks.github_data.graphql_queries import (
    pull_request_graphql_query,
    pull_requests_graphql_query
)
from bitcoin_acks.github_data.repositories_data import RepositoriesData
from bitcoin_acks.github_data.users_data import UsersData
from bitcoin_acks.logging import log
from bitcoin_acks.models import PullRequests
from bitcoin_acks.models.etl.etl_data import ETLData


class PullRequestsData(RepositoriesData):
    MAX_PRS = 20

    def __init__(self, repository_path: str, repository_name: str, json_data_directory: str):
        super(PullRequestsData, self).__init__(repository_path=repository_path,
                                               repository_name=repository_name)

        self.comments_data = CommentsData(repository_name=self.repo.name,
                                          repository_path=self.repo.path)
        self.users_data = UsersData()
        self.json_data_directory = json_data_directory
        self.pull_request_data = []
        self.review_decisions_data = []
        self.labels_data = []

    def update(self):
        with session_scope() as session:
            try:
                record = (
                    session
                    .query(PullRequests.updated_at)
                    .order_by(PullRequests.updated_at.desc())
                    .limit(1)
                    .one()
                )
                from_date = record.updated_at
            except NoResultFound:
                from_date = datetime(2009, 1, 1)
        log.debug('Updating PRs starting from', from_date=from_date)
        self.update_all(newer_than=from_date)

    def update_from_manual_date(self):
        from_date = datetime(2009, 1, 1)
        log.debug('Updating PRs starting from', from_date=from_date)
        self.update_all(newer_than=from_date)

    def get_one(self, number: int):
        json_object = {
            'query': pull_request_graphql_query,
            'variables': {'prNumber': number}
        }
        data = self.graphql_post(json_object=json_object).json()
        pull_request = data['data']['repository']['pullRequest']
        validated_pull_request_data = pull_request_schema.load(pull_request)
        self.parse_into_queue(validated_pull_request_data)

    def update_all(self,
                   newer_than: datetime,
                   state: PullRequestState = None,
                   limit: int = None):
        log.debug('update_all', state=state, limit=limit, newer_than=newer_than)
        self.get_all(state=state, limit=limit, newer_than=newer_than)

    def get_all(self,
                newer_than: datetime,
                state: PullRequestState = None,
                limit: int = None):
        log.debug('get_all', state=state, limit=limit, newer_than=newer_than)
        variables = {}
        received = 0
        ends_at = newer_than
        while limit is None or received < limit:
            if limit is None:
                variables['prFirst'] = self.MAX_PRS
            else:
                variables['prFirst'] = min(limit - received, self.MAX_PRS)

            if state is not None:
                variables['prState'] = state.value

            formatted_ends_at = ends_at.replace(microsecond=0).astimezone(pytz.utc).isoformat()
            variables['searchQuery'] = f'type:pr updated:>={formatted_ends_at} repo:bitcoin/bitcoin sort:updated-asc'

            log.debug('Variables for graphql pull requests query', variables=variables)
            json_object = {
                'query': pull_requests_graphql_query,
                'variables': variables
            }

            response = self.graphql_post(json_object=json_object)
            data = response.json()
            try:
                search_data = data['data']['search']
            except KeyError:
                log.error('Error in response', response=response.text)
                raise
            pull_requests_graphql_data = search_data['edges']
            results_count = len(search_data['edges'])

            log.debug(
                'response from github graphql',
                results_count=results_count
            )
            if not results_count:
                break

            starts_at = pull_requests_graphql_data[0]['node']['updatedAt']
            previous_ends_at = ends_at
            ends_at = parse(pull_requests_graphql_data[-1]['node']['updatedAt'])
            if previous_ends_at == ends_at:
                break
            log.debug(
                'Pull requests fetched',
                starts_at=starts_at,
                ends_at=ends_at
            )

            pull_requests_graphql_data = [r['node'] for r in pull_requests_graphql_data if r['node']]

            for pull_request_graphql in pull_requests_graphql_data:
                validated_pull_request_data = pull_request_schema.load(pull_request_graphql)
                self.parse_into_queue(validated_pull_request_data)
                if limit is not None and received == limit:
                    break
                received += 1
            self.flush_queue_to_database()

    def parse_into_queue(self, pull_request: dict):
        pull_request['repository_id'] = self.repo.id
        comments = pull_request.pop('comments')
        reviews = pull_request.pop('reviews')
        comments_and_reviews = []
        if comments['totalCount'] > 100 or reviews['totalCount'] > 100:
            comments_and_reviews += [
                c for c in self.comments_data.get_all(pull_request['number'])
            ]
        else:
            comments_and_reviews += comments['nodes'] + reviews['nodes']
        for comment_or_review in comments_and_reviews:
            comment_or_review['review_decision'] = self.comments_data.identify_review_decision(
                comment_or_review['bodyText']
            )
            if comment_or_review['review_decision'] != ReviewDecision.NONE:
                comment_or_review['pull_request_id'] = pull_request['id']
                if not comment_or_review['id']:
                    comment_or_review['id'] = comment_or_review['url']
                self.review_decisions_data.append(comment_or_review)

        project_items = pull_request.pop('projectItems')
        high_priority_for_review = [project_item for project_item in project_items['nodes']
                                    if project_item['project']
                                    and project_item['project']['title'] == 'High-priority for review']

        if high_priority_for_review and (pull_request['closedAt'] or high_priority_for_review[0]['isArchived']):
            pull_request['is_high_priority'] = high_priority_for_review[0]['createdAt']
            pull_request['added_to_high_priority'] = high_priority_for_review[0]['createdAt']
            pull_request['removed_from_high_priority'] = high_priority_for_review[0]['updatedAt']
        elif high_priority_for_review:
            pull_request['is_high_priority'] = high_priority_for_review[0]['createdAt']
            pull_request['added_to_high_priority'] = high_priority_for_review[0]['createdAt']
            pull_request['removed_from_high_priority'] = None
        else:
            pull_request['is_high_priority'] = None
            pull_request['added_to_high_priority'] = None
            pull_request['removed_from_high_priority'] = None

        # Last commit is used to determine CI status
        last_commit_status = None
        commits = pull_request.pop('commits')
        pull_request['commit_count'] = commits['totalCount']
        head_commit_hash = pull_request['headRefOid']
        if commits['nodes']:
            last_commit = [c for c in commits['nodes'] if c['commit']['oid'] == head_commit_hash][0]['commit']
            last_commit_status = last_commit.get('statusCheckRollup')

        if last_commit_status is not None:
            pull_request['last_commit_state'] = last_commit_status['state'].capitalize()
        else:
            pull_request['last_commit_state'] = None

        if len(commits['nodes']):
            pull_request['last_commit_short_hash'] = commits['nodes'][-1]['commit']['oid'][0:7]
            pull_request['last_commit_pushed_date'] = commits['nodes'][-1]['commit']['pushedDate']
        else:
            pull_request['last_commit_short_hash'] = None
            pull_request['last_commit_pushed_date'] = None

        labels = pull_request.pop('labels')
        for label in labels['nodes']:
            label['pull_request_id'] = pull_request['id']
            self.labels_data.append(label)
        self.pull_request_data.append(pull_request)

    def flush_queue_to_database(self):
        for file_name, data_list, data_insert_function in [
            ('pull_request_data.json', self.pull_request_data, self.insert_pull_requests),
            ('review_decisions_data.json', self.review_decisions_data, self.insert_comments_and_reviews),
            ('labels_data.json', self.labels_data, self.insert_labels)
        ]:
            if not len(data_list):
                continue
            json_path = os.path.join(self.json_data_directory, file_name)
            with open(json_path, 'w') as json_file:
                for item in data_list:
                    item = flatten_json(item)
                    for key in item.keys():
                        if isinstance(item[key], str) and key not in ('author_login', 'id', 'pull_request_id', 'name',
                                                                      'url'):
                            if key == 'id':
                                print(item[key])
                            input_string = item[key]
                            item[key] = ' '.join([re.sub(r'\W+', '', s) for s in input_string.split()]).replace('"', '')
                    string = json.dumps(item, ensure_ascii=True, separators=(',', ':'), default=str) + '\n'
                    json_file.write(string)

            with session_scope() as db_session:
                db_session.execute('TRUNCATE etl_data;')
                with open(json_path, 'rb') as fp:
                    postgres_copy.copy_from(fp,
                                            ETLData,
                                            db_session.connection(),
                                            ['data'])
            data_insert_function()

        self.pull_request_data = []
        self.review_decisions_data = []
        self.labels_data = []

    def insert_comments_and_reviews(self):
        with session_scope() as db_session:
            missing_authors = db_session.execute(
                """
SELECT DISTINCT etl_data.data ->> 'author_login'
FROM etl_data
         LEFT OUTER JOIN users ON etl_data.data ->> 'author_login' = users.login
WHERE users.id IS NULL;
                """
            ).fetchall()

        if missing_authors:
            log.debug('missing_authors', missing_authors=missing_authors, count=len(missing_authors))

        for author in missing_authors:
            login = author[0]
            if login is None:
                continue
            user_data = self.users_data.get(login)
            self.users_data.upsert(user_data)

        with session_scope() as db_session:
            db_session.execute(
                """
WITH etl_data AS (
    SELECT DISTINCT etl_data.data ->> 'id'                                                  AS id,
                    etl_data.data ->> 'bodyText'                                            AS body,
                    (etl_data.data ->> 'publishedAt')::timestamp with time zone                            AS published_at,
                    etl_data.data ->> 'url'                                                 AS url,
                    etl_data.data ->> 'pull_request_id'                                     AS pull_request_id,
                    users.id                                                                AS author_id,
                    split_part(etl_data.data ->> 'review_decision', '.', 2)::reviewdecision AS auto_detected_review_decision
    FROM etl_data
             LEFT OUTER JOIN users
                             ON etl_data.data ->> 'author_login' = users.login
)
INSERT
INTO comments (id,
               body,
               published_at,
               url,
               pull_request_id,
               author_id,
               auto_detected_review_decision)
SELECT *
FROM etl_data
ON CONFLICT (id) DO UPDATE SET id = excluded.id,
                               body                          = excluded.body,
                               published_at                  = excluded.published_at,
                               url                           = excluded.url,
                               pull_request_id               = excluded.pull_request_id,
                               author_id                     = excluded.author_id,
                               auto_detected_review_decision = excluded.auto_detected_review_decision
;
                """
            )
        with session_scope() as db_session:
            db_session.execute(
                """
WITH etl_data AS (
    SELECT DISTINCT etl_data.data ->> 'pull_request_id' AS pull_request_id FROM etl_data
)
UPDATE pull_requests
SET review_decisions_count = s.review_decisions_count,
    stale_tested_ack_count = s.stale_tested_ack_count,
    fresh_tested_ack_count = s.fresh_tested_ack_count,
    untested_ack_count = s.untested_ack_count,
    concept_ack_count = s.concept_ack_count,
    nack_count = s.nack_count
from (SELECT count(comments.id) as review_decisions_count,
             sum(CASE WHEN comments.auto_detected_review_decision = 'TESTED_ACK'::reviewdecision 
                        AND pull_requests.last_commit_short_hash IS NOT NULL
                         AND comments.body LIKE '%' || pull_requests.last_commit_short_hash || '%' THEN 1 ELSE 0 END) 
                            as fresh_tested_ack_count,
             sum(CASE WHEN comments.auto_detected_review_decision = 'TESTED_ACK'::reviewdecision 
                        AND pull_requests.last_commit_short_hash IS NULL
                         OR comments.body NOT LIKE '%' || pull_requests.last_commit_short_hash || '%' THEN 1 ELSE 0 END) 
                            as stale_tested_ack_count,
             sum(CASE WHEN comments.auto_detected_review_decision = 'UNTESTED_ACK'::reviewdecision THEN 1 ELSE 0 END) 
                            as untested_ack_count,
             sum(CASE WHEN comments.auto_detected_review_decision = 'CONCEPT_ACK'::reviewdecision THEN 1 ELSE 0 END) 
                            as concept_ack_count,
             sum(CASE WHEN comments.auto_detected_review_decision = 'NACK'::reviewdecision THEN 1 ELSE 0 END) 
                            as nack_count,
             etl_data.pull_request_id
      FROM etl_data
               LEFT JOIN comments on etl_data.pull_request_id = comments.pull_request_id AND
                                     comments.auto_detected_review_decision is not null and
                                     comments.auto_detected_review_decision != 'NONE'::reviewdecision
               LEFT JOIN pull_requests on etl_data.pull_request_id = pull_requests.id
      GROUP BY etl_data.pull_request_id) s
WHERE s.pull_request_id = pull_requests.id;
                """
            )

    @staticmethod
    def insert_labels():
        with session_scope() as db_session:
            db_session.execute(
                """
WITH etl_data AS (
    SELECT DISTINCT etl_data.data ->> 'id'              AS id,
                    etl_data.data ->> 'name'            AS "name",
                    etl_data.data ->> 'color'           AS color
    FROM etl_data
)
INSERT
INTO labels (id,
             "name",
             color)
SELECT id, name, color FROM etl_data
ON CONFLICT (id) DO UPDATE SET name  = excluded.name,
                               color = excluded.color;

DELETE FROM pull_requests_labels WHERE pull_request_id IN (
SELECT etl_data.data ->> 'pull_request_id' AS pull_request_id FROM etl_data);

WITH etl_data AS (
    SELECT DISTINCT etl_data.data ->> 'id'              AS label_id,
                    etl_data.data ->> 'pull_request_id' AS pull_request_id
    FROM etl_data
             LEFT OUTER JOIN pull_requests_labels
                             ON etl_data.data ->> 'id' = pull_requests_labels.label_id
                                 AND etl_data.data ->> 'pull_request_id' = pull_requests_labels.pull_request_id
    WHERE pull_requests_labels.id IS NULL
)
INSERT
INTO pull_requests_labels (label_id,
                           pull_request_id)
SELECT label_id, pull_request_id FROM etl_data;
                """
            )

    def insert_pull_requests(self):
        with session_scope() as db_session:
            missing_authors = db_session.execute(
                """
SELECT DISTINCT epr.data ->> 'author_login'
FROM etl_data epr
         LEFT OUTER JOIN users authors ON epr.data ->> 'author_login' = authors.login
WHERE authors.id IS NULL;
                """
            ).fetchall()

        if missing_authors:
            log.debug('missing_authors', missing_authors=missing_authors, count=len(missing_authors))

        for author in missing_authors:
            login = author[0]
            if login is None:
                continue
            user_data = self.users_data.get(login)
            self.users_data.upsert(user_data)

        with session_scope() as db_session:
            db_session.execute("""
WITH etl_data AS (
    SELECT DISTINCT epr.data ->> 'id'                                      AS id,
                    epr.data ->> 'repository_id'                           AS repository_id,
                    author.id                                              AS author_id,
                    (epr.data ->> 'number')::int                           AS "number",
                    epr.data ->> 'state'                                   AS "state",
                    epr.data ->> 'title'                                   AS title,
                    (epr.data ->> 'createdAt')::timestamp with time zone                  AS created_at,
                    (epr.data ->> 'updatedAt')::timestamp with time zone                  AS updated_at,
                    (epr.data ->> 'is_high_priority')::timestamp with time zone           AS is_high_priority,
                    (epr.data ->> 'added_to_high_priority')::timestamp with time zone     AS added_to_high_priority,
                    (epr.data ->> 'removed_from_high_priority')::timestamp with time zone AS removed_from_high_priority,
                    (epr.data ->> 'additions')::int                        AS additions,
                    (epr.data ->> 'deletions')::int                        AS deletions,
                    epr.data ->> 'mergeable'                               AS mergeable,
                    epr.data ->> 'last_commit_state'                       AS last_commit_state,
                    epr.data ->> 'last_commit_short_hash'                  AS last_commit_short_hash,
                    (epr.data ->> 'last_commit_pushed_date')::timestamp with time zone    AS last_commit_pushed_date,
                    epr.data ->> 'bodyText'                                AS body,
                    (epr.data ->> 'mergedAt')::timestamp with time zone                   AS merged_at,
                    (epr.data ->> 'closedAt')::timestamp with time zone                   AS closed_at,
                    (epr.data ->> 'commit_count')::int                     AS commit_count
    FROM etl_data epr
             LEFT OUTER JOIN users author
                             ON epr.data ->> 'author_login' = author.login
)
INSERT
INTO pull_requests (id,
                    repository_id,
                    author_id,
                    "number",
                    "state",
                    title,
                    created_at,
                    updated_at,
                    is_high_priority,
                    added_to_high_priority,
                    removed_from_high_priority,
                    additions,
                    deletions,
                    mergeable,
                    last_commit_state,
                    last_commit_short_hash,
                    last_commit_pushed_date,
                    body,
                    merged_at,
                    closed_at,
                    commit_count)
SELECT *
FROM etl_data
ON CONFLICT ON CONSTRAINT pull_requests_unique_constraint DO UPDATE SET repository_id                 = excluded.repository_id,
                                                                        author_id                     = excluded.author_id,
                                                                        "number"                      = excluded.number,
                                                                        "state"                       = excluded.state,
                                                                        title                         = excluded.title,
                                                                        created_at                    = excluded.created_at,
                                                                        updated_at                    = excluded.updated_at,
                                                                        is_high_priority              = excluded.is_high_priority,
                                                                        added_to_high_priority        = excluded.added_to_high_priority,
                                                                        removed_from_high_priority    = excluded.removed_from_high_priority,
                                                                        additions                     = excluded.additions,
                                                                        deletions                     = excluded.deletions,
                                                                        mergeable                     = excluded.mergeable,
                                                                        last_commit_state             = excluded.last_commit_state,
                                                                        last_commit_short_hash        = excluded.last_commit_short_hash,
                                                                        last_commit_pushed_date       = excluded.last_commit_pushed_date,
                                                                        body                          = excluded.body,
                                                                        merged_at                     = excluded.merged_at,
                                                                        closed_at                     = excluded.closed_at,
                                                                        commit_count                  = excluded.commit_count
;""")


def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out
