"""
'yafi_fetch' master

1.  This script download the instrument list from SGX.
2.  It then parses the list for tickers.
3.  Tickers are then written to the 'yafi_fetch' queue.
"""

import json
import logging
import os
import sys
import time

import pika
from logger import Logger


EXCHANGE_NAME = 'financial_instrument'
ROUTING_KEY = "yafi.fetch"
QUEUE_NAME = 'yafi_fetch'


def setup_rabbit_mq(channel):
    channel.exchange_declare(
        exchange=EXCHANGE_NAME, 
        exchange_type='topic')
        
    channel.queue_declare(
        queue=QUEUE_NAME, 
        durable=True)
    
    channel.queue_bind(
        exchange=EXCHANGE_NAME, 
        routing_key=ROUTING_KEY,
        queue=QUEUE_NAME)


def publish_tickers(url_parameters, ticker_list):

    with pika.BlockingConnection(url_parameters) as connection, connection.channel() as channel:

        setup_rabbit_mq(channel)

        for ticker in ticker_list:

            channel.basic_publish(
                exchange=EXCHANGE_NAME, 
                routing_key=ROUTING_KEY, 
                body=ticker,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ))

            log.info(f"Publish {ticker}", event="publish", type="ticker", target=ticker)
        

def get_tickers_from_instrument_list():
    log.info("Parse SGX instrument list", source="program", event="parse", target="ticker", data_source="SGX instrument list")
    return ['BN4', 'C09']


def download_sgx_instrument_list():
    log.info("Download SGX instrument list", source="program", event="download", target="SGX instrument list")


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


def setup_logging():
    logging.getLogger('pika').setLevel(logging.WARNING)
    log = Logger()
    return log

if __name__ == "__main__":
    log = setup_logging()
    url_parameters = get_cloudamqp_url_parameters()
    download_sgx_instrument_list()
    ticker_list = get_tickers_from_instrument_list()
    # filter ticker_list with blacklist
    publish_tickers(url_parameters, ticker_list)
    log.info("Program complete", source="program", event="complete")