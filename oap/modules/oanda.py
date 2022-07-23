import json
import logging
import requests
from os import path

class OandaApi(object):
    def __init__(self, secrets, app_path):
        self.api_key = secrets['api_key']
        self.api_url = secrets['api_url']
        self.streaming_api_url = secrets['streaming_api_url']
        self.account_id = secrets['account_id']
        self.app_path = app_path
        self.headers={
            'Authorization': f"Bearer {self.api_key}"
        }

    def dump_to_file(self, file_name, json_data):
        out_file_path = path.join(self.app_path, 'data-dump', file_name)
        with open(out_file_path, 'w', encoding='UTF8') as out_file:
            out_file.write(json.dumps(json_data, indent=4))

    def get_from_file(self, file_name):
        out_file_path = path.join(self.app_path, 'data-dump', file_name)
        with open(out_file_path, 'r', encoding='UTF8') as in_file:
            return json.load(in_file)

    def get_all_account(self):
        """
        Get all accounts
        """
        response = requests.get(
                f"{self.api_url}/v3/accounts", 
                headers=self.headers)
        response_json = response.json()
        account_list = response_json['accounts']
        logging.debug(account_list)

    def get_account_summary(self, account_id=None):
        """
        Get account summary
        """
        account_id = self.account_id if account_id is None else account_id
        response = requests.get(
                f"{self.api_url}/v3/accounts/{account_id}/summary", 
                headers=self.headers)
        response_json = response.json()
        logging.debug(response_json)
        self.dump_to_file('account-summary.json', response_json)
        return response_json
        

    def get_account_instruments(self, account_id=None, get_local=False):
        """
        Get account summary
        """
        if get_local:
            return self.get_from_file('account-instruments.json')

        account_id = self.account_id if account_id is None else account_id
        response = requests.get(
                f"{self.api_url}/v3/accounts/{account_id}/instruments", 
                headers=self.headers)
        response_json = response.json()
        logging.debug(response_json)
        self.dump_to_file('account-instruments.json', response_json)
        return response_json

    def get_latest_candles(self, candle_spec, account_id=None):
        account_id = self.account_id if account_id is None else account_id
        response = requests.get(
                f"{self.api_url}/v3/accounts/{account_id}/candles/latest?candleSpecifications={candle_spec}", 
                headers=self.headers)
        response_json = response.json()
        logging.debug(response_json)
        
        normalized_candle_spec = candle_spec.replace(':','-')
        self.dump_to_file(f'latest-candles-{normalized_candle_spec}.json', response_json)
        return response_json

    def get_account_candles(self, instrument_name, granularity='D', account_id=None):
        account_id = self.account_id if account_id is None else account_id
        response = requests.get(
                f"{self.api_url}/v3/accounts/{account_id}/instruments/{instrument_name}/candles?granularity={granularity}", 
                headers=self.headers)
        response_json = response.json()
        logging.debug(response_json)
        
        # normalized_candle_spec = candle_spec.replace(':','-')
        self.dump_to_file(f'account-candles-{instrument_name}-{granularity}.json', response_json)
        return response_json