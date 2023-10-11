# pyright: reportMissingImports=false

import logging
import boto3
import json
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def download_script(event):
    print('Downloading Script')
    s3.download_file(event['Script_Details']['Bucket_Name'], event['Script_Details']['File_Name'], '/tmp/script.txt')
    
    script = '/tmp/script.txt'
    return script

def Generate_Polly_Payload(script):
    payload = {}

    # Using readlines()
    script_file = open(script, 'r')
    Lines = script_file.readlines()
    print('number of lines in script: {}'.format(len(Lines)))
    
    Polly_Payload = ''
    Polly_Payload+='<speak>'
    Scene_Count = 0
    # Strips the newline character
    for line in Lines:
        print('First char in line {} is {}'.format(Scene_Count, line[0:10]))
        if line[0:10] == 'Narrator: ':
            new_line = ''
            new_line+='<p>'
            new_line+=line[10:-1]
            new_line+='</p>'
            new_line+='\n'

            Polly_Payload+=new_line
        elif line[0] == '[':
            new_line = ''
            new_line+='<mark name="scene{}"/>'.format(Scene_Count)
            new_line+='\n'

            Polly_Payload+=new_line
            Scene_Count+=1

    Polly_Payload+='</speak>'
    print(Polly_Payload)

    return Polly_Payload

def Upload_Polly_Payload(polly_payload, JobId):
    local_path = "/tmp/"

    file = open(local_path + "polly_payload.txt", "w")
    file.write(str(polly_payload))
    file.close()

    with open(local_path + "polly_payload.txt", 'rb') as f:
        s3.upload_fileobj(f, os.environ['ArtefactBucket'], '/{}/polly_payload.txt'.format(JobId))
        f.close()

    response = {
        "Polly_Details": {
            "Bucket_Name": os.environ['ArtefactBucket'],
            "File_Name": '/{}/polly_payload.txt'.format(JobId)
        }
    }

    return response

def lambda_handler(event, context):
    print("context: {}".format(context))
    print("Event: {}".format(event))

    script = download_script(event)
    polly_payload = Generate_Polly_Payload(script)
    response = Upload_Polly_Payload(polly_payload, event['Job_Id'])

    Job_Details = dict(event)
    Job_Details.update(response)

    return Job_Details