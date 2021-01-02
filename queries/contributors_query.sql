SELECT
       dev.login,
       to_char( pr.earliest_pull_request, 'MM/DD/YYYY') AS earliest_pull_request,
       date_part('day', now() - pr.earliest_pull_request) AS days_since_earliest_pull_request,
       to_char( pr.latest_pull_request, 'MM/DD/YYYY') AS latest_pull_request,
       date_part('day', now() - pr.latest_pull_request) AS days_since_latest_pull_request,
       to_char( c.earliest_comment, 'MM/DD/YYYY') AS earliest_comment,
       date_part('day', now() - c.earliest_comment) AS days_since_earliest_comment,
       to_char( c.latest_comment, 'MM/DD/YYYY') AS latest_comment,
       date_part('day', now() - c.latest_comment) AS days_since_latest_comment,
       pr.total_pull_request_count,
       pr.merged_pull_request_count,
       c.nacks,
       c.concept_acks,
       c.untested_acks,
       c.tested_acks,
       c.nacks + c.concept_acks + c.untested_acks + c.tested_acks as total_reviews,
       c.nonreview_comments
FROM users dev
LEFT OUTER JOIN
  (
    SELECT
              author_id,
              min(pull_requests.created_at) AS earliest_pull_request,
              max(pull_requests.created_at) AS latest_pull_request,
              count(id) AS total_pull_request_count,
              sum(CASE WHEN merged_at is not null THEN 1 ELSE 0 END) AS merged_pull_request_count
    FROM pull_requests
    GROUP BY author_id
  ) pr on dev.id = pr.author_id
LEFT OUTER JOIN
  (
   SELECT
          author_id,
          min(comments.published_at) as earliest_comment,
          max(comments.published_at) as latest_comment,
          sum(CASE WHEN comments.auto_detected_review_decision = 'NACK'::reviewdecision THEN 1 ELSE 0 END) AS nacks,
          sum(CASE WHEN comments.auto_detected_review_decision = 'CONCEPT_ACK'::reviewdecision THEN 1 ELSE 0 END) AS concept_acks,
          sum(CASE WHEN comments.auto_detected_review_decision = 'UNTESTED_ACK'::reviewdecision THEN 1 ELSE 0 END) AS untested_acks,
          sum(CASE WHEN comments.auto_detected_review_decision = 'TESTED_ACK'::reviewdecision THEN 1 ELSE 0 END) AS tested_acks,
          sum(CASE WHEN comments.auto_detected_review_decision = 'NONE'::reviewdecision THEN 1 ELSE 0 END) AS nonreview_comments
   FROM comments
   GROUP BY author_id
  ) c ON c.author_id = dev.id
ORDER BY merged_pull_request_count DESC NULLS LAST;