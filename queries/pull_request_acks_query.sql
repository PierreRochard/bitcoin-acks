SELECT
       pr.number,
       pr.state,
       authors.login AS author,
       pr.additions,
       pr.deletions,
       to_char( created_at, 'MM/DD/YYYY') AS created_at_day,
       to_char( created_at, 'MM/YYYY') AS created_at_month,
       date_part('day', NOW() - pr.created_at) AS days_since_created,
       to_char( updated_at, 'MM/DD/YYYY') AS updated_at_day,
       to_char( updated_at, 'MM/YYYY') AS updated_at_month,
       date_part('day', pr.updated_at - pr.created_at) AS days_between_created_and_updated,
       to_char( merged_at, 'MM/DD/YYYY') AS merged_at_day,
       to_char( merged_at, 'MM/YYYY') AS merged_at_month,
       date_part('day', pr.merged_at - pr.created_at) AS days_between_created_and_merged,
       to_char( closed_at, 'MM/DD/YYYY') AS closed_at_day,
       to_char( closed_at, 'MM/YYYY') AS closed_at_month,
       date_part('day', pr.closed_at - pr.created_at) AS days_between_created_and_closed,
       coalesce(reviews.total_reviews, 0) as total_reviews,
       coalesce(reviews.nacks, 0) as nacks,
       coalesce(reviews.concept_acks, 0) as concept_acks,
       coalesce(reviews.untested_acks, 0) as untested_acks,
       coalesce(reviews.tested_acks, 0) as tested_acks,
       to_char( pr.added_to_high_priority, 'MM/DD/YYYY') AS added_to_high_priority,
       to_char( pr.removed_from_high_priority, 'MM/DD/YYYY') AS removed_from_high_priority,
       date_part('day', coalesce(pr.removed_from_high_priority, now()) - pr.added_to_high_priority) AS days_in_high_priority
FROM pull_requests pr
LEFT OUTER JOIN users authors ON pr.author_id = authors.id
LEFT OUTER JOIN
       (
         SELECT
                pull_request_id,
                count(id) AS total_reviews,
                sum(CASE WHEN comments.auto_detected_review_decision = 'NACK'::reviewdecision THEN 1 ELSE 0 END) AS nacks,
                sum(CASE WHEN comments.auto_detected_review_decision = 'CONCEPT_ACK'::reviewdecision THEN 1 ELSE 0 END) AS concept_acks,
                sum(CASE WHEN comments.auto_detected_review_decision = 'UNTESTED_ACK'::reviewdecision THEN 1 ELSE 0 END) AS untested_acks,
                sum(CASE WHEN comments.auto_detected_review_decision = 'TESTED_ACK'::reviewdecision THEN 1 ELSE 0 END) AS tested_acks

         FROM comments
         WHERE comments.auto_detected_review_decision != 'NONE'::reviewdecision
         GROUP BY pull_request_id
         ) reviews ON reviews.pull_request_id = pr.id
-- WHERE added_to_high_priority IS NOT NULL
ORDER BY pr.number DESC;