import json
import logging
import os
import sys


# os.system("source /opt/conda/bin/activate envname")

import boto3
import botocore
import cv2
import subprocess
import ffmpeg
import shutil



from video_processor import apply_faces_to_video, integrate_audio

logger = logging.getLogger()
logger.setLevel(logging.INFO)

reko = boto3.client('rekognition')
s3 = boto3.client('s3')

output_bucket = 'project-videostore'


def convert_to_h264(input_file, output_file):
    try:
        ffmpeg.input(input_file).output(output_file, codec='libx264').run()
    except Exception as e:
        print(e)

def get_timestamps_and_faces(job_id):
    final_timestamps = {}
    next_token = "Y"
    first_round = True
    while next_token != "":
        print('.', end='')
        # Set some variables if it's the first iteration
        if first_round:
            next_token = ""
            first_round = False
        # Query Reko Video
        response = reko.get_face_detection(JobId=job_id, MaxResults=100, NextToken=next_token)
        print('response')
        print(response)
        # Iterate over every face
        for face in response['Faces']:
            f = face["Face"]["BoundingBox"]
            t = str(face["Timestamp"])
            time_faces = final_timestamps.get(t)
            if time_faces == None:
                final_timestamps[t] = []
            final_timestamps[t].append(f)
        # Check if there is another portion of the response
        try:
            next_token = response['NextToken']
        except:
            break
    # Return the final dictionary
    print('Complete')
    return final_timestamps, response

def lambda_function(event, context):
    # download file locally to /tmp retrieve metadata
    try:
        platform = sys.platform
        print('platform')
        print(platform)
        print('ffmpeg')
        print(ffmpeg)
        ffmpeg_path = shutil.which("ffmpeg")
        print('which ffmpeg')
        print(ffmpeg_path)
        timestamps, response = get_timestamps_and_faces('aac512fe9c6431a8876de131d43637711abb96df167c3b24446cef243986c2c2')
        print('Final response => ')
        print(response)
        print('final timestamps')
        print(timestamps)
        # get metadata of file uploaded to Amazon S3
        bucket = 'project-videostore'
        key = 'people3trim(orignal)_24_fps.mp4'
        filename = key
        local_filename = '/tmp/{}'.format(filename)
        local_filename_output = '/tmp/anonymized-{}'.format(filename)
        local_codec_output = '/tmp/codec/anonymized-{}'.format(filename)
    except KeyError:
        error_message = 'Lambda invoked without S3 event data. Event needs to reference a S3 bucket and object key.'
        logger.log(logging.ERROR, error_message)
        # add_failed(bucket, error_message, failed_records, key)

    try:
        s3.download_file(bucket, key, local_filename)

        # Retrieve the MIME type (ContentType) of the object
        metaData = s3.head_object(Bucket=bucket, Key=key)
        mime_type = metaData['ContentType']
        print('The mime of downloaded video --')
        print(mime_type)
    except botocore.exceptions.ClientError:
        error_message = 'Lambda role does not have permission to call GetObject for the input S3 bucket, or object does not exist.'
        logger.log(logging.ERROR, error_message)
        # add_failed(bucket, error_message, failed_records, key)
        # continue

        # get timestamps
    try:
        print('face blur start')
        apply_faces_to_video(timestamps, local_filename, local_filename_output, response["VideoMetadata"])
        print('face blur done !!')
    except Exception as e:
        print(e)
        # continue

    # try:
    #     integrate_audio(local_filename, local_filename_output)
    # except Exception as e:
    #     print(e)

    # uploaded modified video to Amazon S3 bucket
    try:
        print('ffmpeg process started')
        print('input file name => ')
        print(local_filename_output)
        print('output file name')
        print(local_codec_output)
        convert_to_h264(local_filename_output, local_codec_output)
        print('ffmpeg process end !')
        s3.upload_file(local_codec_output, output_bucket, 'blurredxx-'+key, ExtraArgs={'ContentType': mime_type})
        # s3.upload_file(local_filename_output, output_bucket, 'blurredxx-'+key)
    except boto3.exceptions.S3UploadFailedError:
        error_message = 'Lambda role does not have permission to call PutObject for the output S3 bucket.'
        # add_failed(bucket, error_message, failed_records, key)
        # continue

    return {
        'statusCode': 200,
        'body': json.dumps('Faces in video blurred')
    }
