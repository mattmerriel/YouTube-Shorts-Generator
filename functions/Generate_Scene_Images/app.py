# pyright: reportMissingImports=false

import logging
import boto3
import base64
import json
import os
import io
from PIL import Image

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('bedrock-runtime')
s3 = boto3.client('s3')

def Generate_Image(scene_description, Scene_Number, JobId):

    bedrock_payload = json.dumps({
        "text_prompts": [
            {"text": scene_description}
        ], 
        "cfg_scale": 10,
        "seed": 0,
        "steps": 50
    })  

    print("Submitted BedRock Payload: {}".format(bedrock_payload))

    response = client.invoke_model(
        accept='application/json',
        body=bedrock_payload,
        contentType='application/json',
        modelId='stability.stable-diffusion-xl'
    )

    filename = "/tmp/{}.png".format(Scene_Number)

    response_body = json.loads(response['body'].read())
    base_64_img_str = response_body.get("artifacts")[0].get("base64")

    image = Image.open(io.BytesIO(base64.decodebytes(bytes(base_64_img_str, "utf-8"))))
    image.save(filename)

    return filename

def Upload_Image(Image, Scene_number, JobId):
    with open("/tmp/{}.png".format(Scene_number), 'rb') as f:
        s3.upload_fileobj(f, os.environ['ArtefactBucket'], '/{}/scenes/{}.png'.format(JobId, Scene_number))
        f.close()

    return

def lambda_handler(event, context):
    print("context: {}".format(context))
    print("Event: {}".format(event))

    scene_image = Generate_Image(event['Scene_Description'], event['Scene_Count'], event["Job_Id"])
    Upload_Image(scene_image, event['Scene_Count'], event["Job_Id"])
    return event