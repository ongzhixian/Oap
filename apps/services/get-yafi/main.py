
import json
import logging
import os
import sys
import urllib.request

import pika
from logger import Logger
from os import path


QUEUE_NAME = 'yafi_fetch'

def blacklist(ticker):
    logging.warn(f"TODO: Blacklist ticker {ticker}.")

def fetch_chart_json_from_yafi(yami_ticker, range='max', granularity='1mo'):
    app_path = ''
    logging.info(f"Fetching chart data from YAFI: {yami_ticker}")
    data_file_name = f'{yami_ticker}-{range}-{granularity}.json'
    out_file_path = path.join(app_path, 'data-dump', data_file_name)
    if path.exists(out_file_path):
        return True # Skip
    # There are a couple of URLs used to get the SGX data from Yahoo Finance.
    # https://query1.finance.yahoo.com/v8/finance/chart/BN4.SI
    api_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yami_ticker}?range={range}&granularity={granularity}"
    request = urllib.request.Request(api_url)
    # try:
    #     with urllib.request.urlopen(request) as response:
    #         json_data = json.loads(response.read().decode("utf-8"))
    #     dump_json_data_to_file(data_file_name, json_data)
    #     return True
    # except Exception:
    #     return False

def download_yafi_chart_json(ticker):
    if not fetch_chart_json_from_yafi(ticker):
        blacklist(ticker)

def process_message(channel, method, properties, body):
    text_content = body.decode('utf-8')
    download_yafi_chart_json(text_content)
    channel.basic_ack(delivery_tag=method.delivery_tag)
    log.info("Received message", source="program", event="receive", content=text_content)


def listen_for_tickers(url_parameters):
    with pika.BlockingConnection(url_parameters) as connection, connection.channel() as channel:
        channel.queue_declare(
            queue=QUEUE_NAME, 
            durable=True)
        
        channel.basic_consume(
            queue=QUEUE_NAME, 
            on_message_callback=process_message)

        log.info("Listen to queue", source="program", event="listen", target=QUEUE_NAME)
        channel.start_consuming()


def get_cloudamqp_url_parameters():

    if len(sys.argv) < 1:
        exit(1)
    
    full_path = os.path.abspath(sys.argv[1])
    
    if not os.path.exists(full_path):
        exit(2)
    
    try:
        with open(full_path, "r", encoding="utf-8") as in_file:
            json_data = json.load(in_file)
    except Exception:
        exit(3)
    
    if 'cloud_amqp' not in json_data:
        exit(4)
    if 'armadillo' not in json_data['cloud_amqp']:
        exit(4)
    if 'url' not in json_data['cloud_amqp']['armadillo']:
        exit(4)
    
    cloud_amqp_url = json_data['cloud_amqp']['armadillo']['url']

    log.info("Cloud AMQP URL read", source="program", event="set", target="cloud amqp url")
    
    return pika.URLParameters(cloud_amqp_url)


def load_settings():
    app_path = path.dirname(path.abspath(__file__))
    settings_file_path = path.join(app_path, 'settings.json')
    if not path.exists(settings_file_path):
        print(f"Settings file ({settings_file_path}) missing.")
        exit(1)
    with open(settings_file_path, 'r', encoding='utf8') as app_settings_file:
        app_settings_json = json.load(app_settings_file)
    app_settings_json['app_path'] = app_path
    return app_settings_json


def setup_logging():
    logging.getLogger('pika').setLevel(logging.WARNING)
    log = Logger()
    return log

def get_chart_json_out_path():
    if len(sys.argv) < 2:
        exit(1)
    
    full_path = os.path.abspath(sys.argv[2])
    if not path.exists(full_path):
        try:
            pass
            # Ensure path is create
            os.makedirs(full_path)
        except:
            exit(6)

    log.info("Chart JSON output path", source="program", event="set", target="chart json out path", path=full_path)

    return full_path


if __name__ == "__main__":
    settings = load_settings()
    log = setup_logging()
    url_parameters = get_cloudamqp_url_parameters()
    chart_json_out_path = get_chart_json_out_path()
    # listen_for_tickers(url_parameters)
    
    print("All ok")
