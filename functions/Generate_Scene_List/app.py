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

def Generate_Scenes(script, Job_Id):

    # Using readlines()
    script_file = open(script, 'r')
    Lines = script_file.readlines()
    print('number of lines in script: {}'.format(len(Lines)))
    
    count = 0
    scene_list = {
        "Scenes": []
    }
    # Strips the newline character
    for line in Lines:
        print('First char in line {} is {}'.format(count, line[0]))
        if line[0] == '[':
            scene_payload = line.split(': ', 1)
            scene = {
                'Job_Id': Job_Id,
                'Scene_Count': count,
                'Line': line,
                'Scene_Type': scene_payload[0].strip('['),
                'Scene_Description': scene_payload[1][:-4]
            }

            scene_list['Scenes'].append(scene)
            print("Line{}: {}".format(count, line.strip()))
            count += 1

    return scene_list

def lambda_handler(event, context):
    print("context: {}".format(context))
    print("Event: {}".format(event))

    script = download_script(event)
    scenes = Generate_Scenes(script, event['Job_Id'])

    Job_Details = dict(event)
    Job_Details.update(scenes)
    return Job_Details