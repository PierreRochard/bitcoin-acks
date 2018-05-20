import os


def get_query(query_file: str):
    path = os.path.dirname(os.path.abspath(__file__))
    graphql_file = os.path.join(path, query_file)
    with open(graphql_file, 'r') as query_file:
        query = query_file.read()
        return query


comments_graphql_query = get_query('comments.graphql')
pull_request_graphql_query = get_query('pull_request.graphql')
pull_requests_graphql_query = get_query('pull_requests.graphql')
reviews_graphql_query = get_query('reviews.graphql')
user_graphql_query = get_query('user.graphql')
