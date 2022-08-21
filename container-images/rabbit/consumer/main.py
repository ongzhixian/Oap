
import json
import logging
import os
import sys

import pika
from logger import Logger


QUEUE_NAME = 'yafi_fetch'


def process_message(channel, method, properties, body):
    text_content = body.decode('utf-8')
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


def setup_logging():
    logging.getLogger('pika').setLevel(logging.WARNING)
    log = Logger()
    return log

if __name__ == "__main__":
    log = setup_logging()
    url_parameters = get_cloudamqp_url_parameters()
    listen_for_tickers(url_parameters)
