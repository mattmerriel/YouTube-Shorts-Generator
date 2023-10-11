# pyright: reportMissingImports=false

import logging
import boto3
import json
import os
import math
import copy
import csv

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')

def Download_Voice_Mark(Bucket_Name, File_Name):
    print('Downloading Script')
    s3.download_file(Bucket_Name, File_Name, '/tmp/VoiceOver_Marks.txt')
    
    payload = '/tmp/VoiceOver_Marks.txt'
    return payload

def Generate_Frame_Schedule(marks, Job_Id, Bucket_Name):
    MARKDOWN_LIST = []
    
    with open(marks) as fp:
        MARKUP_LIST = fp.readlines()
        for x in MARKUP_LIST:
            MARKDOWN_LIST.append(json.loads(x))
        fp.close()    

    VIDEO_LENGTH_MS = MARKDOWN_LIST[-1]['time'] + 2000
    VIDEO_LENGTH_S = VIDEO_LENGTH_MS/1000
    VIDEO_LENGTH_FRAMES = math.ceil(VIDEO_LENGTH_S * 30)
    print('Video Length is {} milliseonds or {} seconds'.format(VIDEO_LENGTH_MS, VIDEO_LENGTH_S))
    print('Total number of frames is: {}'.format(math.ceil(VIDEO_LENGTH_FRAMES)))



    LAST_ANIMATED_FRAME = 0
    CURRENT_FRAME = 0

    for x in MARKDOWN_LIST:
        if x['type'] == 'ssml':
            CURRENT_FRAME = int(math.ceil((x['time'] // 33.3333333333333) + 1))           
            print("current frame is: {}".format(CURRENT_FRAME))
    TEMPLATE_FRAME = {}
    TEMPLATE_FRAME['id'] = 0
    TEMPLATE_FRAME['Job_Id'] = Job_Id
    TEMPLATE_FRAME['background'] = 'black'
    TEMPLATE_FRAME['image'] = ''  

    FRAME_ARRAY = []

    for x in MARKDOWN_LIST:

        ANIMATION_REQUIRED = False

        CURRENT_FRAME = copy.deepcopy(TEMPLATE_FRAME)

        print(x)

        if x['type'] == "ssml":
            ANIMATION_REQUIRED = True
            CURRENT_FRAME['id'] = int(math.ceil((x['time'] // 33.3333333333333) + 1))
            CURRENT_FRAME['image'] = x['value'][5:]+'.png'
            CURRENT_FRAME['background'] = 'black'
    
        if ANIMATION_REQUIRED:
            for MISSING_FRAMES in range(LAST_ANIMATED_FRAME + 1, CURRENT_FRAME['id']):
                if MISSING_FRAMES == 1:
                    FILLER_FRAME = copy.deepcopy(TEMPLATE_FRAME)
                else:
                    FILLER_FRAME = copy.deepcopy(FRAME_ARRAY[-1])
                FILLER_FRAME['id'] = MISSING_FRAMES
                FRAME_ARRAY.append(FILLER_FRAME)
                LAST_ANIMATED_FRAME = MISSING_FRAMES
            FRAME_ARRAY.append(CURRENT_FRAME)
            LAST_ANIMATED_FRAME = CURRENT_FRAME['id']

    CSV_FIELD_NAMES = ['id', 'Job_Id', 'background', 'image']
    with open('/tmp/frame_schedule.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELD_NAMES)
        writer.writeheader()
        writer.writerows(FRAME_ARRAY)

    with open('/tmp/frame_schedule.csv', 'rb') as f:
        s3.upload_fileobj(f, Bucket_Name, '/{}/schedule.csv'.format(Job_Id))
        f.close()

    response = {
        "Schedule_Details": {
            "Bucket_Name": os.environ['ArtefactBucket'],
            "File_Name": '/{}/schedule.csv'.format(Job_Id)
        }
    }

    return response

def lambda_handler(event, context):
    print("context: {}".format(context))
    print("Event: {}".format(event))

    Voice_Marks = Download_Voice_Mark(event['VoiceOver_Marks_Details']['Bucket_Name'], event['VoiceOver_Marks_Details']['File_Name'])
    Schedule_Response = Generate_Frame_Schedule(Voice_Marks, event['Job_Id'], event['VoiceOver_Marks_Details']['Bucket_Name'])

    Job_Details = dict(event)
    Job_Details.update(Schedule_Response)
    return Job_Details