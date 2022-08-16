import logging
import json
from urllib.request import Request, urlopen

def save_file(out_file_path, data):
    with open(out_file_path, 'w', encoding='UTF8') as out_file:
        out_file.write(data)

def save_data_from_url(src_url, save_file_path):
    logging.debug(f"Saving data from {src_url} to {save_file_path}")
    
    try:
        request = Request(src_url)
        with urlopen(request) as response:
            breakpoint()
            save_file(save_file_path, response.read().decode("utf-8"))
        return True
    except Exception as e:
        print(e)
        return False