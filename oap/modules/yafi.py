import json
import logging
import requests
from os import path
import urllib.request


class YaFiApi(object):
    def __init__(self, secrets, app_path):
        self.app_path = app_path

    def dump_to_file(self, file_name, json_data):
        out_file_path = path.join(self.app_path, 'data-dump', file_name)
        with open(out_file_path, 'w', encoding='UTF8') as out_file:
            out_file.write(json.dumps(json_data, indent=4))

    def get_sgx_data(self, yami_ticker):
        # There are a couple of URLs used to get the SGX data from Yahoo Finance.
        # https://query1.finance.yahoo.com/v8/finance/chart/BN4.SI
        api_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yami_ticker}"
        request = urllib.request.Request(api_url)
        with urllib.request.urlopen(request) as response:
            json_data = json.loads(response.read().decode("utf-8"))
        # Save the JSON data
        self.dump_to_file(f'{yami_ticker}.json', json_data)
        # chart_json = json_data['chart']
        # result = chart_json['result'][0]
        # meta = chart_json['result'][0]['meta']
        # timestamp = chart_json['result'][0]['timestamp']
        # indicators = chart_json['result'][0]['indicators']
