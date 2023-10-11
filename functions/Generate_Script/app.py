# pyright: reportMissingImports=false

import logging
import boto3
from datetime import datetime
import json
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('bedrock-runtime')
s3 = boto3.client('s3')

def generate_script(subject):

    prompt = "you are a writer for a new educational YouTube channel focused on producing 60 second YouTube shorts videos. As a part of writing these new videos you need to write both the narrators script as well as call out when scenes should change and what they should change too. When calling out a new scene, make sure to wrap the information on a new line, surrounded by square brackets, and when referencing a person or location... make sure to use the whole name (first and last name or town and state). The generated script must start by defining the opening scene is as well so there are no parts of the video that are unclear as to the scene design. Based on that, produce a video on {}".format(subject)
    bedrock_payload = json.dumps({
        "prompt": prompt, 
        "maxTokens": 8191,
        "stopSequences":[],
        "temperature":0,
        "topP":0.9
    })  

    print("Submitted BedRock Payload: {}".format(bedrock_payload))

    response = client.invoke_model(
        accept='application/json',
        body=bedrock_payload,
        contentType='application/json',
        modelId='ai21.j2-ultra-v1'
    )

    response_body = json.loads(response['body'].read())
    script = response_body['completions'][0]['data']['text']

    print("and the script is: {}".format(script))
    return script

def get_timestamp():
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")

    return timestamp

def upload_script(script, JobId):
    local_path = "/tmp/" + JobId + "/"

    # Check whether the specified path exists or not
    isExist = os.path.exists(local_path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(local_path)
        print("The new directory is created!")


    file = open(local_path + "script.txt", "w")
    file.write(str(script))
    file.close()

    with open(local_path + "script.txt", 'rb') as f:
        s3.upload_fileobj(f, os.environ['ArtefactBucket'], '/{}/script.txt'.format(JobId))
        f.close()

    response = {
        "Script_Details": {
            "Bucket_Name": os.environ['ArtefactBucket'],
            "File_Name": '/{}/script.txt'.format(JobId)
        }
    }
    return response

def lambda_handler(event, context):
    print("Context: {}".format(context))
    print("Event: {}".format(event))

    str_array = str(event['Video_Subject'])

    script = generate_script(str_array)
    upload_Response = upload_script(script, event["Job_Id"])

    Job_Details = dict(event)
    Job_Details.update(upload_Response)

    return Job_Details