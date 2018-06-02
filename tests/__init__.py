import os

tests_directory = os.path.dirname(os.path.realpath(__file__))
fixtures_data_directory = os.path.join(tests_directory, 'fixtures_data')
issues_file_path = os.path.join(fixtures_data_directory, 'issues.json')
pull_requests_file_path = os.path.join(fixtures_data_directory, 'pull_requests_{state}_{limit}.json')
pull_request_file_path = os.path.join(fixtures_data_directory, 'pull_request.json')
