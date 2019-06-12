from typing import List

from sqlalchemy import func, and_
from sqlalchemy.orm.exc import NoResultFound

from bitcoin_acks.constants import ReviewDecision
from bitcoin_acks.database import session_scope
from bitcoin_acks.github_data.graphql_queries import (
    comments_graphql_query,
    reviews_graphql_query
)
from bitcoin_acks.github_data.repositories_data import RepositoriesData
from bitcoin_acks.github_data.users_data import UsersData
from bitcoin_acks.models import Comments


class CommentsData(RepositoriesData):
    def __init__(self, repository_path: str, repository_name: str):
        super(CommentsData, self).__init__(repository_path=repository_path,
                                           repository_name=repository_name)

    @staticmethod
    def get_review_count(pull_request_id: str, pull_request_author_id) -> int:
        with session_scope() as session:
            review_count = (
                session.query(func.count(Comments.id))
                .filter(
                    and_(
                        Comments.pull_request_id == pull_request_id,
                        Comments.review_decision != ReviewDecision.NONE,
                        Comments.author_id != pull_request_author_id
                    )
                ).scalar()
            )
            return review_count

    def get_all(self, pull_request_number: int):
        for query, nested_name in (
                (comments_graphql_query, 'comments'),
                (reviews_graphql_query, 'reviews')):
            received_count = 0
            first_cursor = None
            variables = {
                'commentsLast': 100,
                'prNumber': pull_request_number
            }
            while True:
                if first_cursor is not None:
                    variables['commentsCursorBefore'] = first_cursor

                json_object = {
                    'query': query,
                    'variables': variables
                }

                data = self.graphql_post(json_object=json_object).json()

                results = data['data']['repository']['pullRequest'][nested_name]
                expected_count = results['totalCount']
                if not expected_count:
                    break
                comments = results['edges']
                received_count += len(comments)

                first_cursor = comments[0]['cursor']

                comments = [c['node'] for c in comments]
                for comment in comments:
                    yield comment

                if received_count >= expected_count:
                    break

    @staticmethod
    def identify_review_decision(text: str) -> ReviewDecision:
        text = text.lower()
        if 'concept ack' in text or 're-ack' in text:
            return ReviewDecision.CONCEPT_ACK
        elif 'tested ack' in text:
            return ReviewDecision.TESTED_ACK
        elif 'utack' in text or 'untested ack' in text:
            return ReviewDecision.UNTESTED_ACK
        elif 'tack ' in text:
            return ReviewDecision.TESTED_ACK
        elif 'nack' in text:
            return ReviewDecision.NACK
        elif text.startswith('ack '):
            return ReviewDecision.TESTED_ACK
        else:
            return ReviewDecision.NONE

    def upsert(self, pull_request_id: str, data: dict) -> bool:
        data['body'] = data['body'].replace('\x00', '')
        review_decision = self.identify_review_decision(data['body'])

        author = data.pop('author')
        author_id = UsersData().upsert(data=author)

        with session_scope() as session:
            try:
                record = (
                    session.query(Comments)
                        .filter(Comments.id == data['id'])
                        .one()
                )
            except NoResultFound:
                record = Comments()
                record.pull_request_id = pull_request_id
                record.author_id = author_id
                session.add(record)

            for key, value in data.items():
                setattr(record, key, value)
            record.auto_detected_review_decision = review_decision

        if review_decision == ReviewDecision.NONE:
            return False
        return True

    def bulk_upsert(self, pull_request_id: str, comments: List[dict]):
        ack_comment_authors = []
        comments = sorted(comments,
                          key=lambda k: k['publishedAt'],
                          reverse=True)
        comments = [c for c in comments if c['body'] and c['author'] is not None]
        for comment in comments:
            comment_author_name = comment['author']['login']
            if comment_author_name not in ack_comment_authors:
                is_review_decision = self.upsert(pull_request_id=pull_request_id,
                                                 data=comment)
                if is_review_decision:
                    ack_comment_authors.append(comment_author_name)


if __name__ == '__main__':
    comments_data = CommentsData(repository_name='bitcoin',
                                 repository_path='bitcoin')
    comments = [c for c in comments_data.get_all(pull_request_number=10637)]
    print(len(comments))
