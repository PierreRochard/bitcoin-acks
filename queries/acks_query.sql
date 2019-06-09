SELECT ack.id,
       pull_requests.number AS pull_request_number,
       reviewer.login,
       auto_detected_review_decision,
       published_at,
       to_char( published_at, 'MM/DD/YYYY') AS published_at_day,
       to_char( published_at, 'MM/YYYY') AS published_at_month,
       ack.body

FROM comments ack
LEFT OUTER JOIN users reviewer ON reviewer.id = ack.author_id
LEFT OUTER JOIN pull_requests ON pull_requests.id = ack.pull_request_id
WHERE ack.auto_detected_review_decision != 'NONE'::reviewdecision;