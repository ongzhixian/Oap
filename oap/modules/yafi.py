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
        data_file_name = f'{yami_ticker}-{range}-{granularity}.json'
        out_file_path = path.join(self.app_path, 'data-dump', data_file_name)
        if path.exists(out_file_path):
            return True # Skip
        # There are a couple of URLs used to get the SGX data from Yahoo Finance.
        # https://query1.finance.yahoo.com/v8/finance/chart/BN4.SI
        api_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yami_ticker}?range={range}&granularity={granularity}"
        request = urllib.request.Request(api_url)
        try:
            with urllib.request.urlopen(request) as response:
                json_data = json.loads(response.read().decode("utf-8"))
            # Save the JSON data
            self.dump_to_file(data_file_name, json_data)
            return True
        except Exception:
            return False


    def debug_sgx(self):
        json_data = self.get_from_file(f'C09.SI-max-1mo.json')
        chart_json = json_data['chart']
        result = chart_json['result'][0]
        meta = chart_json['result'][0]['meta']
        timestamp = chart_json['result'][0]['timestamp']
        indicators = chart_json['result'][0]['indicators']
        ohlcv = indicators['quote'][0]
        qopen = indicators['quote'][0]['open']
        qclose = indicators['quote'][0]['close']
        qhigh = indicators['quote'][0]['high']
        qlow = indicators['quote'][0]['low']
        qvolume = indicators['quote'][0]['volume']
        qadjclose = indicators['adjclose'][0]['adjclose']
        # So to properly transpose, we should iterate over the timestamp
        # Ya! And think about how the transpose should work for reading the values
        # Ideally, we want to re-format the data into this format: ['time','complete', 'Volume', 'Open', 'High', 'Low', 'Close']
        import time
        
        d_list = []
        for i in range(len(timestamp)):
            # print(timestamp[i], volume[i], open[i], close[i], high[i], low[i], adjclose[i])
            d = (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp[i])), qvolume[i], qopen[i], qhigh[i], qlow[i], qclose[i], qadjclose[i])
            d_list.append(d)
        # time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1183219200))
        import csv
        with open('./data-dump/C09.SI-max-1mo.csv', 'w', encoding='utf8', newline='') as out_file:
            csv_writer = csv.writer(out_file)
            csv_writer.writerows(d_list)


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

# https://query1.finance.yahoo.com/v7/finance/quote?symbols=C09.SI&fields=exchangeTimezoneName,exchangeTimezoneShortName,regularMarketTime,gmtOffSetMilliseconds&region=US&lang=en-US
# https://query1.finance.yahoo.com/v7/finance/quote?formatted=true&crumb=ANSQqUYemPa&lang=en-US&region=US&symbols=C09.SI&fields=messageBoardId,longName,shortName,marketCap,underlyingSymbol,underlyingExchangeSymbol,headSymbolAsString,regularMarketPrice,regularMarketChange,regularMarketChangePercent,regularMarketVolume,uuid,regularMarketOpen,fiftyTwoWeekLow,fiftyTwoWeekHigh,toCurrency,fromCurrency,toExchange,fromExchange&corsDomain=finance.yahoo.com
# https://query2.finance.yahoo.com/v10/finance/quoteSummary/C09.SI?formatted=true&crumb=ANSQqUYemPa&lang=en-US&region=US&modules=summaryProfile,financialData,recommendationTrend,upgradeDowngradeHistory,defaultKeyStatistics,calendarEvents,esgScores,details&corsDomain=finance.yahoo.com

# https://query1.finance.yahoo.com/v7/finance/spark?symbols=RTY=F&range=1d&interval=5m&indicators=close&includeTimestamps=false&includePrePost=false&corsDomain=finance.yahoo.com&.tsrc=finance
# https://query1.finance.yahoo.com/v6/finance/recommendationsbysymbol/C09.SI


# https://query1.finance.yahoo.com/v8/finance/chart/C09.SI?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance
# https://query1.finance.yahoo.com/v7/finance/spark?symbols=CL=F&range=1d&interval=5m&indicators=close&includeTimestamps=false&includePrePost=false&corsDomain=finance.yahoo.com&.tsrc=finance



# GoFi
# https://www.google.com/finance/quote/C09:SGX


# Reuters?
# https://www.reuters.com/markets/companies/ETEL.SI