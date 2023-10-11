# pyright: reportMissingImports=false

import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_timestamp():
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")

    return timestamp

def lambda_handler(event, context):
    guid = get_timestamp()
    
    response = {}
    response["Job_Id"] = guid
    response["Video_Subject"] = event["subject"]

    return response