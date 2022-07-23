import json
import logging

from time import sleep
from os import path
from oap import app
from oap.modules.oanda import OandaApi

def setup_default_logging():
    try:
        console_logger = logging.StreamHandler()
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.NOTSET)
        root_logger.addHandler(console_logger)
        logging.debug("Default logging configured.")
    except Exception as e:
        logging.error(e)


def get_secrets(app_path):
    app_secrets_path = path.join(app_path, 'app-secrets.json')
    with open(app_secrets_path, 'r', encoding='utf8') as app_settings_file:
        return json.load(app_settings_file)


setup_default_logging()
app_path = path.dirname(path.abspath(__file__))
app_secrets = get_secrets(app_path)

oandaApi = OandaApi(app_secrets, app_path)
# oandaApi.get_account_summary()
x = oandaApi.get_account_instruments(get_local=True)
instruments = x['instruments']

for instrument in instruments:
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


# for instrument in instruments:
#     logging.debug(instrument['name'])
#     instrument_name = instrument['name']
#     oandaApi.get_account_candles(instrument_name, 'D')
#     sleep(1)

# candle_spec = 'EUR_USD:D:M'
# oandaApi.get_latest_candles(candle_spec)


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=32000, debug=True)
