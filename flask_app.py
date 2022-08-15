import json
import logging

import argparse

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

def dump_instrument_class(instrument_list):
    d_list = []
    for instrument in instrument_list:
        tags = instrument['tags']
        tag_map = {}
        for tag in tags:
            tag_map[tag['type']] = tag['name']
        
        asset_class = None
        if 'ASSET_CLASS' in tag_map:
            asset_class = tag_map['ASSET_CLASS']

        kid_asset_class = None
        if 'KID_ASSET_CLASS' in tag_map:
            kid_asset_class = tag_map['KID_ASSET_CLASS']

        d = (instrument['name'], 
            instrument['displayName'], 
            instrument['type'],
            asset_class,
            kid_asset_class)
        # logging.debug(instrument['name'])
        # logging.debug(instrument['displayName'])
        # logging.debug(instrument['type'])
        logging.debug(d)
        d_list.append(d)
    import csv
    
    with open('./data-dump/oda-simplified-instruments.csv', 'w', encoding='utf8', newline='') as out_file:
        csv_writer = csv.writer(out_file)
        csv_writer.writerows(d_list)


def fetch_candles_data(instrument_list):
    for instrument in instrument_list:
        logging.debug(instrument['name'])
        instrument_name = instrument['name']
        oandaApi.get_account_candles(instrument_name, 'D')
        sleep(1)
    pass


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
    # request.files
    # ImmutableMultiDict([('upload_file', <FileStorage: 'XAU_USD-close-plot.png' (None)>)])

    # The other correct way if you want more control
    # files = {'upload_file': ('foobar.txt', open('file.txt','rb'), 'text/x-spam')}

    values = {
        'DB': 'photcat', 
        'OUT': 'csv', 
        'SHORT': 'short'
    }
    # Values would be accessible like so in Flask:
    # request.form['DB']
    # ImmutableMultiDict([('DB', 'photcat'), ('OUT', 'csv'), ('SHORT', 'short')])

    r = requests.post(url, files=files, data=values)

# def analysis2():
#     from datetime import datetime
#     import pandas as pd
#     # import matplotlib.pyplot as plt
#     import mplfinance as mpf

#     with open('./data-dump/account-candles-XAU_USD-D.json', 'r', encoding='UTF8') as in_file:
#         json_data = json.load(in_file)

#     candles = json_data['candles']
#     flatten_data = [
#         [ 
#             datetime.strptime(x['time'], "%Y-%m-%dT%H:%M:%S.%f000Z"), 
#             bool(x['complete']), 
#             int(x['volume']), 
#             float(x['mid']['o']), 
#             float(x['mid']['h']), 
#             float(x['mid']['l']), 
#             float(x['mid']['c'])
#         ] for x in candles]
#     df = pd.DataFrame(
#         flatten_data, 
#         columns=['time','complete', 'Volume', 'Open', 'High', 'Low', 'Close'])

#     df['ma'] = df['Close'].rolling(20).mean()
#     df['ewm'] = df['Close'].ewm(span=20, adjust=False).mean()

#     print(f"df shape: {df.shape}")

#     dfx = df.tail(50).set_index('time')
#     mpf.plot(dfx, type='line', 
#         mav=(20, 39),
#         hlines=dict(hlines=[1850,1865],colors=['g','r'],linestyle='-.',linewidths=(1,1)),
#         volume=True,
#         savefig='./pic-dump/sample.png')

################################################################################


def dump_oanda_charts(post=False):
    setup_default_logging()

    # oandaApi.get_account_summary()
    x = oandaApi.get_account_instruments(get_local=True)
    instruments = x['instruments']

    fetch_candles_data(instruments)
    # dump_instrument_class(instruments)

    for instrument in instruments:
        dump_chart_for_instrument(instrument['name'], instrument['displayName'])

    if post:
        for instrument in instruments:
            post_chart(instrument['name'])


def get_argument_parser():
    # Setup ArgumentParser
    parser = argparse.ArgumentParser()
    # parser.add_argument("command", help="echo the string you use here")
    parser.add_argument("-c", "--command", choices=['dump-oanda', 'test'], help="Some operation command")
    parser.add_argument("-a", "--arguments", help="Some arguments to complement command")
    # parser.add_argument("-v", "--verbosity", type=int, help="increase output verbosity")
    # parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], help="increase output verbosity")
    # parser.add_argument("-v", "--verbosity", action="count", default=0, help="increase output verbosity")
    # parser.add_argument("echo", help="echo the string you use here")
    # parser.add_argument("square", help="display a square of a given number", type=int)
    return parser


parser = get_argument_parser()
args = parser.parse_args()

# print(args.command)
# print(args.sub_command)
# print(args.echo)
# print(args.square**2)

print(f'Command: [{args.command}]')

def test():
    print('test() called.')

# import sys
# print('Number of arguments:', len(sys.argv), 'arguments.')
# print('Argument List:', str(sys.argv))

########################################

app_path = path.dirname(path.abspath(__file__))
app_secrets = get_secrets(app_path)

oandaApi = OandaApi(app_secrets, app_path)

commands = {
    'dump-oanda' : dump_oanda_charts,
    'test': test
}

commands[args.command]()














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
