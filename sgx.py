import json
import logging
import re
import argparse

from time import sleep
from os import path, remove
from oap import app
from oap.modules.oanda import OandaApi

import urllib.parse

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

from oap.modules.inet import save_data_from_url

def get_instrument_list_from_sgx():
    # Note: We cannot use Python request to get the data from SGX;
    #       We get a HTTP 403 (Forbidden) response.
    #       Not sure if its because of headers or the request itself (missing cookies?).
    #       In any case, KIV for now.
    #       Assuming that we were able to get the file and store in as sgx-isin.txt
    #       D:\src\github\oap\data-dump\sgx
    logging.info("Getting ISINs from SGX (v0)")
    # url = 'https://links.sgx.com/1.0.0/isin/1/16 Aug 2022'
    # today = quote(datetime.today().strftime('%d %b %Y'))
    # url = f'https://links.sgx.com/1.0.0/isin/1/{today}'
    # url = 'https://links.sgx.com/FileOpen/01%20Aug%202022.ashx?App=ISINCode&FileID=1&FileType=csv'
    # save_file_path = path.join(app_path, 'data-dump', 'sgx-isin.dat')
    # logging.info("1. Get SGX list of instruments")
    # save_data_from_url(url, save_file_path)
    # logging.info(url)
    # logging.info(save_file_path)

def get_tickers_from_isin_file():
    in_file_path = path.join(app_path, 'data-dump', 'sgx', 'sgx-isin.txt')
    if not path.exists(in_file_path):
        logging.error(f'File missing: {in_file_path}')

    ticker_list = []
    sgx_isin_layout = r"(?P<name>.{50})(?P<status>.{10})(?P<isin>.{20})(?P<code>.{10})(?P<counter>.+)"
    with open(in_file_path, 'r', encoding='UTF8') as in_file:
        in_file.readline() # skip first header line
        for line in in_file:
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
        data = []
        for ticker in ticker_list:
            data.append((ticker, ticker))
        sql = """
INSERT INTO ticker (name) 
SELECT 	? AS 'name'
WHERE	NOT EXISTS (SELECT 1 FROM ticker WHERE 	name = ?)
"""
        connection_cursor.executemany(sql, data)

    # Insert a row of data
    # cur.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

    # Save (commit) the changes
    # connection.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    # connection.close()


################################################################################

app_path = path.dirname(path.abspath(__file__))
app_secrets = get_secrets(app_path)

setup_default_logging()

from urllib.parse import quote

# SGX Data Feed
# Steps:
# 1. Get SGX list of instruments (ISINs)
# 2. Get counters from ISIN file
get_instrument_list_from_sgx()
ticker_list = get_tickers_from_isin_file()
add_tickers_to_database(ticker_list)

