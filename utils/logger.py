import logging.config
import os
from datetime import datetime
import json

def set_up_log(book_name):
    # Set up logging

    app_name = 'relationship_network'
    logs_path = './logs/'

    # Create log path if it does not exist
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    # The name of the file changes every day
    filename = datetime.today().strftime('%y%m%d') + '_' + book_name + '_' + app_name + '.log'

    # Format the log
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(asctime)s - %(message)s',   
        handlers=[
            logging.FileHandler(os.path.join(logs_path, filename)),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__) 