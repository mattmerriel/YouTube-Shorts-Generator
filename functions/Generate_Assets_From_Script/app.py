# pyright: reportMissingImports=false

import logging
import boto3
import json
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("context: {}".format(context))
    print("Event: {}".format(event))

    return event