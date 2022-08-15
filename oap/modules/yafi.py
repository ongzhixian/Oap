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

    def get_from_file(self, file_name):
        out_file_path = path.join(self.app_path, 'data-dump', file_name)
        with open(out_file_path, 'r', encoding='UTF8') as in_file:
            return json.load(in_file)

    def get_sgx_data(self, yami_ticker, range='max', granularity='1mo'):
        # There are a couple of URLs used to get the SGX data from Yahoo Finance.
        # https://query1.finance.yahoo.com/v8/finance/chart/BN4.SI
        api_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yami_ticker}?range={range}&granularity={granularity}"
        request = urllib.request.Request(api_url)
        with urllib.request.urlopen(request) as response:
            json_data = json.loads(response.read().decode("utf-8"))
        # Save the JSON data
        self.dump_to_file(f'{yami_ticker}-{range}-{granularity}.json', json_data)
        # chart_json = json_data['chart']
        # result = chart_json['result'][0]
        # meta = chart_json['result'][0]['meta']
        # timestamp = chart_json['result'][0]['timestamp']
        # indicators = chart_json['result'][0]['indicators']

    def debug_sgx(self):
        json_data = self.get_from_file(f'BN4.SI-max-1mo.json')
        chart_json = json_data['chart']
        result = chart_json['result'][0]
        meta = chart_json['result'][0]['meta']
        timestamp = chart_json['result'][0]['timestamp']
        indicators = chart_json['result'][0]['indicators']
        ohlcv = indicators['quote'][0]
        open = indicators['quote'][0]['open']
        close = indicators['quote'][0]['close']
        high = indicators['quote'][0]['high']
        low = indicators['quote'][0]['low']
        adjclose = indicators['adjclose'][0]['adjclose']
        # So to properly transpose, we should iterate over the timestamp
        # Ya! And think about how the transpose should work for reading the values
        breakpoint()
        # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1183219200))


# https://query1.finance.yahoo.com/v8/finance/chart/BN4.SI?region=US&lang=en-US&includePrePost=false&interval=1mo&useYfid=true&range=max&corsDomain=finance.yahoo.com&.tsrc=finance

# The default URL is:
# https://query1.finance.yahoo.com/v8/finance/chart/BN4.SI
# This default pulls in the range of 1d (1 day), in 1m (1 minute) granularity
# "dataGranularity": "1m",
# "range": "1d",
# Valid ranges: 
# "1d",     -- 
# "5d",     --
# "1mo",    --
# "3mo",    --
# "6mo",    --
# "1y",     --
# "2y",     --
# "5y",     --
# "10y",    --
# "ytd",    --
# "max"     --