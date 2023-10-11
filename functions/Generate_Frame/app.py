# pyright: reportMissingImports=false

import logging
import json
import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def Download_Image(image, Job_Id):
    print('Downloading Image')
    s3.download_file(os.environ['ArtefactBucket'], '/' + Job_Id + '/scenes/' + image, '/tmp/{}'.format(image))
    
    script = '/tmp/{}'.format(image)
    return script

def lambda_handler(event, context):

    print("context: {}".format(context))
    print("Event: {}".format(event))

    PAYLOAD = event
    print("Test output")
    for item in PAYLOAD['Items']:
        print('Processing image {}'.format(item['id']))
        FRAME_ID = "%08d" % int((item['id']))
        IMAGE_NAME = FRAME_ID + ".png"
        FILE_PATH = '/tmp/' + item['Job_Id'] + '/' + IMAGE_NAME

        Path('/tmp/' + item['Job_Id']).mkdir(parents=True, exist_ok=True)
        
        img = Image.new('RGBA', (1080, 1920), color = item['background'])


        # Check whether the required images has been downloaded from S3
        if item['image'] == '':
            item['image'] = '0.png'
        isExist = os.path.exists('/tmp/' + item['image'])
        if not isExist:
            # Download file because it does not exist
            Download_Image(item['image'], item['Job_Id'])
            print("Missing Image Downloaded")       

        scene_image = Image.open('/tmp/{}'.format(item['image'])).convert("RGBA")  

        final_image = img.copy()
        final_image.paste(scene_image, (1024,1024), scene_image)

        final_image.save(FILE_PATH)
        try:
            s3_client = boto3.client('s3')
            BUCKET_NAME = os.environ['ArtefactBucket']
            OBJECT_NAME = '/' + item['Job_Id'] + '/frames/' + IMAGE_NAME
            response = s3_client.upload_file(FILE_PATH, BUCKET_NAME, OBJECT_NAME)
            print('Processing for Image {} complete'.format(item['id']))
        except ClientError as e:
            logging.error(e)
            return False



    return event