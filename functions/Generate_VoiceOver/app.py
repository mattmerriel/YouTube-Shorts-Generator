# pyright: reportMissingImports=false

import logging
import boto3
import json
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def Download_Polly_Payload(Bucket_Name, key):
    print('Downloading Script')
    s3.download_file(Bucket_Name, key, '/tmp/polly_payload.txt')
    
    payload = '/tmp/polly_payload.txt'
    return payload

def Generate_VoiceOver_Audio(payload):
    with open(payload, 'r') as f:
        SSML = f.read()
        f.close()   

    client = boto3.client('polly')
    polly_audio_response = client.synthesize_speech(
        Engine='neural',
        OutputFormat='mp3',
        SampleRate='24000',
        Text=SSML,
        TextType='ssml',
        VoiceId='Arthur'
    )

    file = open('/tmp/VoiceOver.mp3', 'wb')
    file.write(polly_audio_response['AudioStream'].read())
    file.close()

    return '/tmp/VoiceOver.mp3'

def Upload_VoiceOver(polly_status, JobId):
    local_path = "/tmp/"

    with open(local_path + "VoiceOver.mp3", 'rb') as f:
        s3.upload_fileobj(f, os.environ['ArtefactBucket'], '/{}/VoiceOver.mp3'.format(JobId))
        f.close()

    response = {
        "VoiceOver_Details": {
            "Bucket_Name": os.environ['ArtefactBucket'],
            "File_Name": '/{}/VoiceOver.mp3'.format(JobId)
        }
    }

    return response

def lambda_handler(event, context):
    print("context: {}".format(context))
    print("Event: {}".format(event))

    polly_payload = Download_Polly_Payload(event['Polly_Details']['Bucket_Name'], event['Polly_Details']['File_Name'])
    polly_status = Generate_VoiceOver_Audio(polly_payload)
    response = Upload_VoiceOver(polly_status, event['Job_Id'])

    Job_Details = dict(event)
    Job_Details.update(response)

    return event