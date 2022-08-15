import json
import logging

from time import sleep
from os import path, remove
from oap import app
from oap.modules.oanda import OandaApi

import pandas as pd
from datetime import datetime

import requests
import matplotlib.pyplot as plt
import mplfinance as mpf


def setup_default_logging():
    try:
        console_logger = logging.StreamHandler()
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)
        root_logger.addHandler(console_logger)
        logging.debug("Default logging configured.")
        # logging.getLogger("mplfinance").setLevel(logging.WARNING)
    except Exception as e:
        logging.error(e)


def get_secrets(app_path):
    app_secrets_path = path.join(app_path, 'app-secrets.json')
    with open(app_secrets_path, 'r', encoding='utf8') as app_settings_file:
        return json.load(app_settings_file)




def dump_chart_for_instrument(instrument, instrument_display_name, ma_period=20, ema_period=20):
    # instrument = 'XAU_USD'
    with open(f'./data-dump/account-candles-{instrument}-D.json', 'r', encoding='UTF8') as in_file:
        json_data = json.load(in_file)
    instrument = json_data['instrument']
    granularity = json_data['granularity']
    candles = json_data['candles']
    flatten_data = [
        [ 
            datetime.strptime(x['time'], "%Y-%m-%dT%H:%M:%S.%f000Z"), 
            bool(x['complete']), 
            int(x['volume']), 
            float(x['mid']['o']), 
            float(x['mid']['h']), 
            float(x['mid']['l']), 
            float(x['mid']['c'])
        ] for x in candles]
    df = pd.DataFrame(
        flatten_data, 
        columns=['time','complete', 'Volume', 'Open', 'High', 'Low', 'Close'])

    df['ma'] = df['Close'].rolling(ma_period).mean()
    df['ewm'] = df['Close'].ewm(span=ema_period, adjust=False).mean()
    index_df = df.set_index('time')

    save_file_path = f'./pic-dump/{instrument}-close-plot.png'
    if path.exists(save_file_path):
        remove(save_file_path) 
    mpf.plot(index_df,type='line', volume=True, title=instrument_display_name, savefig=save_file_path)
    # print(f"df shape: {df.shape}")


def post_chart(instrument):
    pass
    url = 'http://localhost:31000/api/test/upload-file'
    files = {
        'upload_file': open(f'./pic-dump/{instrument}-close-plot.png', 'rb')
    }
    # Files would be accessible like so in Flask:
    values = {
        'DB': 'photcat', 
        'OUT': 'csv', 
        'SHORT': 'short'
    }
    # Values would be accessible like so in Flask:
    # request.form['DB']
    # ImmutableMultiDict([('DB', 'photcat'), ('OUT', 'csv'), ('SHORT', 'short')])
    r = requests.post(url, files=files, data=values)



################################################################################


# def dump_oanda_charts(post=False):
#     setup_default_logging()

#     # oandaApi.get_account_summary()
#     x = oandaApi.get_account_instruments(get_local=True)
#     instruments = x['instruments']

#     fetch_candles_data(instruments)
#     # dump_instrument_class(instruments)

#     for instrument in instruments:
#         dump_chart_for_instrument(instrument['name'], instrument['displayName'])

#     if post:
#         for instrument in instruments:
#             post_chart(instrument['name'])

def get_flatten_data_from_file(symbol):
    with open(f'./data-dump/{symbol}-max-1mo.json', 'r', encoding='UTF8', newline='') as in_file:
        json_data = json.load(in_file)
    
    result_json = json_data['chart']['result'][0]
    meta        = result_json['meta']
    timestamp   = result_json['timestamp']
    quote       = result_json['indicators']['quote'][0]
    quote_open      = quote['open']
    quote_close     = quote['close']
    quote_high      = quote['high']
    quote_low       = quote['low']
    quote_volume    = quote['volume']
    # quote_adj_close = quote['adjclose']

    flatten_data = []
    for i in range(len(timestamp)):
        # print(timestamp[i], volume[i], open[i], close[i], high[i], low[i], adjclose[i])
        d = (
            datetime.fromtimestamp(timestamp[i]), 
            int(quote_volume[i]), 
            float(quote_open[i]), 
            float(quote_high[i]), 
            float(quote_low[i]), 
            float(quote_close[i]))
        flatten_data.append(d)
    return flatten_data


def make_chart(symbol):
    flatten_data = get_flatten_data_from_file(symbol)

    df = pd.DataFrame(
        flatten_data, 
        columns=['time', 'Volume', 'Open', 'High', 'Low', 'Close'])

    index_df = df.set_index('time')

    df['ma'] = df['Close'].rolling(20).mean()
    df['ewm'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # df.head(30)

    save_file_path = f'./pic-dump/{symbol}-close-plot.png'
    if path.exists(save_file_path):
        remove(save_file_path) 
    # mpf.plot(index_df,type='line', volume=True, title=f'{symbol} close', savefig=save_file_path)
    mpf.plot(
        index_df.tail(28),
        type='line', 
        volume=True, 
        savefig=save_file_path, 
        title=f'{symbol} close plot')
    


################################################################################

app_path = path.dirname(path.abspath(__file__))
app_secrets = get_secrets(app_path)

tickers = ['C09']
ymi = 'SI'
for ticker in tickers:
    symbol = f'{ticker}.{ymi}'
    make_chart(symbol)









# setup_default_logging()
# app_path = path.dirname(path.abspath(__file__))
# app_secrets = get_secrets(app_path)

# oandaApi = OandaApi(app_secrets, app_path)
# # oandaApi.get_account_summary()
# x = oandaApi.get_account_instruments(get_local=True)
# instruments = x['instruments']
# fetch_candles_data(instruments)
# # dump_instrument_class(instruments)

# for instrument in instruments:
#     dump_chart_for_instrument(instrument['name'], instrument['displayName'])

# for instrument in instruments:
#     post_chart(instrument['name'])

# KIV
# candle_spec = 'EUR_USD:D:M'
# oandaApi.get_latest_candles(candle_spec)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=32000, debug=True)
