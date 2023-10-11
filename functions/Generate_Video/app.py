# pyright: reportMissingImports=false

import logging
import json
import subprocess
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    print(json.dumps(event))

    FILE_PATH = '/mnt/storage/' + event['JobName']

    s3 = boto3.client('s3')
    s3.download_file(event['JobDetails']['ArtefactBucket'], event['JobDetails']['Recording'], FILE_PATH + "/audio.mp3")

    command = "ffmpeg -r 30 -f image2 -s 1080x1920 -i "+FILE_PATH+"/%08d.png -i "+FILE_PATH+"/audio.mp3 -vcodec libx264 -b 4M -strict -2 "+FILE_PATH+"_final.mp4"
    subprocess.call(command, shell=True)

    s3 = boto3.client('s3')
    with open(FILE_PATH + "_final.mp4", 'rb') as f:
        s3.upload_fileobj(f, os.environ['OutputBucket'], event['JobName'] + '-video.mp4')
        f.close()

    return FILE_PATH