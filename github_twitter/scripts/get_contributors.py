import requests

# contributors_url = 'https://api.github.com/repos/bitcoin/bitcoin/contributors'
# params = {'anon': 1}
# response = requests.get(contributors_url, params=params)
# response_json = response.json()

contributors_url = 'https://api.github.com/repos/bitcoin/bitcoin/stats/contributors'
response = requests.get(contributors_url)
response_json = response.json()
