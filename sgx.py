import json
import logging
import re
import argparse


from time import sleep
from os import path, remove
from oap import app
from oap.modules.oanda import OandaApi

import urllib.request
import urllib.parse
from urllib.parse import quote


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


#####

# def get_data_from_url(self, src_url):
#     api_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yami_ticker}?range={range}&granularity={granularity}"
#     request = urllib.request.Request(api_url)
#     try:
#         with urllib.request.urlopen(request) as response:
#             json_data = json.loads(response.read().decode("utf-8"))
#         # Save the JSON data
#         self.dump_to_file(data_file_name, json_data)
#         return True
#     except Exception:
#         return False

# from oap.modules.inet import save_data_from_url

def get_instrument_list_from_sgx():
    # Note: We cannot use a plain-old Python request to get the data from SGX;
    #       We will get a HTTP 403 (Forbidden) response.
    #       Solution: Add a User-Agent string
    #       Assuming that we were able to get the file and store in as sgx-isin.txt
    #       D:\src\github\oap\data-dump\sgx
    logging.info("Getting ISINs from SGX")
    today = quote(datetime.today().strftime('%d %b %Y'))
    url = f'https://links.sgx.com/1.0.0/isin/1/{today}'
    
    request = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0'
        }
    )

    with urllib.request.urlopen(request) as response:
        sgx_isins = response.read().decode("utf-8")

    out_file_path = path.join(app_path, 'data-dump', 'sgx', 'sgx-isin.txt')
    with open(out_file_path, 'w', encoding='utf-8') as out_file:
        out_file.write(sgx_isins)


def get_tickers_from_isin_file():
    in_file_path = path.join(app_path, 'data-dump', 'sgx', 'sgx-isin.txt')
    if not path.exists(in_file_path):
        logging.error(f'File missing: {in_file_path}')

    ticker_list = []
    sgx_isin_layout = r"(?P<name>.{50})(?P<status>.{10})(?P<isin>.{20})(?P<code>.{10})(?P<counter>.+)"
    with open(in_file_path, 'r', encoding='UTF8') as in_file:
        in_file.readline() # skip first header line
        for line in in_file:
            if len(line.strip()) <= 0:
                continue
            match_result = re.match(sgx_isin_layout, line)
            if match_result is None:
                continue
            code = match_result.group('code').strip()
            ticker_list.append(code)
    logging.info(f"Tickers from SGX: {len(ticker_list)}")
    return ticker_list
    

def ensure_ticker_table_exists(cursor):
    """
    "name"	    INTEGER,
    "type"	    TEXT,
    "status"    INTEGER, # 0 = inactive, 1 = active
    """
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS "ticker" (
        "name"	    TEXT,
        "type"	    TEXT,
        "status"    INTEGER DEFAULT 0,
        PRIMARY KEY("name")
    );''')

def add_tickers_to_database(ticker_list):
    """
    For each ticker in ticker list,
        Check if ticker is in database
            If not, add to database
    """
    in_file_path = path.join(app_path, 'data-dump', 'sgx', 'sgx.sqlite3')
    import sqlite3
    with sqlite3.connect(in_file_path) as connection:
        connection_cursor = connection.cursor()
        ensure_ticker_table_exists(connection_cursor)
        # Insert ticker to database table if not in table
        data = []
        for ticker in ticker_list:
            data.append((ticker, ticker))
        sql = """
INSERT INTO ticker (name) 
SELECT 	? AS 'name'
WHERE	NOT EXISTS (SELECT 1 FROM ticker WHERE 	name = ?);
"""
        connection_cursor.executemany(sql, data)
    logging.info("Add tickers to database")


def get_white_listed_tickers():
    tickers = []
    in_file_path = path.join(app_path, 'data', 'sgx-tickers-whitelist.txt')
    with open(in_file_path, 'r', encoding='UTF8') as in_file:
        for line in in_file:
            tickers.append(line.strip())
    return tickers


def white_list_tickers():
    white_listed_tickers = get_white_listed_tickers()

    in_file_path = path.join(app_path, 'data-dump', 'sgx', 'sgx.sqlite3')
    import sqlite3
    with sqlite3.connect(in_file_path) as connection:
        connection_cursor = connection.cursor()
        ensure_ticker_table_exists(connection_cursor)
        data = []
        for ticker in white_listed_tickers:
            data.append((ticker,))
        sql = """
UPDATE ticker SET status = 1 WHERE name = ?;
"""
        connection_cursor.executemany(sql, data)
    logging.info("White list tickers")
    
def get_yafi_chart_json_data(ticker):
    in_file_path = path.join(app_path, 'data-dump', 'yafi', f'{ticker}.SI-max-1mo.json')
    with open(in_file_path, 'r', encoding='UTF8') as in_file:
        return json.load(in_file)
    return None


def update_instrument_type(sql_update_data):
    in_file_path = path.join(app_path, 'data-dump', 'sgx', 'sgx.sqlite3')
    import sqlite3
    with sqlite3.connect(in_file_path) as connection:
        connection_cursor = connection.cursor()
        sql = """
UPDATE ticker SET type = ? WHERE name = ?;
"""
        connection_cursor.executemany(sql, sql_update_data)


def update_tickers_instrument_type():
    sql_update_data = []
    white_listed_tickers = get_white_listed_tickers()
    for ticker in white_listed_tickers:
        chart_json_data = get_yafi_chart_json_data(ticker)
        meta_json_data = chart_json_data['chart']['result'][0]['meta']
        sql_update_data.append((meta_json_data['instrumentType'], ticker))
    update_instrument_type(sql_update_data)
    logging.info("Update tickers instrument type")
    # YAFI's InstrumentType:
    # BOND       -- No data; maybe because invalid range/data granularity?
    # EQUITY     -- OK
    # ETF        -- OK
    # MUTUALFUND -- OK
    # WARRANT    -- No data; maybe because invalid range/data granularity?


################################################################################

app_path = path.dirname(path.abspath(__file__))
app_secrets = get_secrets(app_path)

setup_default_logging()


# SGX Data Feed
# Steps:
# 1. Get SGX list of instruments (ISINs)
# 2. Get counters from ISIN file
get_instrument_list_from_sgx()
ticker_list = get_tickers_from_isin_file()
add_tickers_to_database(ticker_list)
white_list_tickers()
update_tickers_instrument_type()
