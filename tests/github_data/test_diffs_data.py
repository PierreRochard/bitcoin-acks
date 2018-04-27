import pytest
import requests

from bitcoin_acks.github_data.diffs_data import DiffsData


class TestDiffsData(object):

    @pytest.mark.unit_diffs
    def test_insert_diffs(self, pull_requests_data):
        for data in pull_requests_data[0:100]:
            diff = requests.get(data['diff_url']).text
            DiffsData.insert(data['id'], diff)
