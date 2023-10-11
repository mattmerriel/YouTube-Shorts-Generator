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

def Generate_VoiceOver_Marks(payload):
    with open(payload, 'r') as f:
        SSML = f.read()
        f.close()   

    client = boto3.client('polly')
    polly_audio_response = client.synthesize_speech(
        Engine='neural',
        OutputFormat='json',
        SampleRate='24000',
        Text=SSML,
        TextType='ssml',
        VoiceId='Arthur',
        SpeechMarkTypes=['ssml', 'word']
    )

    audio_data = polly_audio_response['AudioStream'].read().decode('utf-8')
    audio_lines = audio_data.strip().split('\n')

    print(audio_lines)

    speech_marks = []
    for line in audio_lines:
        try:
            mark = json.loads(line)
            speech_marks.append(mark)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")

    with open('/tmp/VoiceOver_Marks.txt', 'w') as txt_file:
        for line in audio_lines:
            txt_file.write(line + "\n")

    return '/tmp/VoiceOver_Marks.txt'

def Upload_VoiceOver(polly_status, JobId):
    local_path = "/tmp/"

    with open(local_path + "VoiceOver_Marks.txt", 'rb') as f:
        s3.upload_fileobj(f, os.environ['ArtefactBucket'], '/{}/VoiceOver_Marks.txt'.format(JobId))
        f.close()

    response = {
        "VoiceOver_Marks_Details": {
            "Bucket_Name": os.environ['ArtefactBucket'],
            "File_Name": '/{}/VoiceOver_Marks.txt'.format(JobId)
        }
    }

    return response

def lambda_handler(event, context):
    print("context: {}".format(context))
    print("Event: {}".format(event))

    polly_payload = Download_Polly_Payload(event['Polly_Details']['Bucket_Name'], event['Polly_Details']['File_Name'])
    polly_status = Generate_VoiceOver_Marks(polly_payload)
    response = Upload_VoiceOver(polly_status, event['Job_Id'])

    Job_Details = dict(event)
    Job_Details.update(response)

    return Job_Details