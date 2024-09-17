import boto3
import cv2
import os
import time

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

# Constants
BUCKET_NAME = 'project-videostore'

def download_video_from_s3(bucket, video_key, download_path):
    """Download video from S3 to /tmp/"""
    s3.download_file(bucket, video_key, download_path)
    print(f"Video downloaded from S3: {video_key}")

def upload_video_to_s3(local_file, bucket, output_key):
    """Upload video to S3 from /tmp/"""
    s3.upload_file(local_file, bucket, output_key)
    print(f"Blurred video uploaded to S3: {output_key}")

def get_face_detection_results(job_id):
    """Retrieve face detection results from AWS Rekognition"""
    while True:
        response = rekognition.get_face_detection(JobId=job_id)
        status = response['JobStatus']
        
        if status == 'SUCCEEDED':
            print(f"Face detection succeeded for Job ID: {job_id}")
            return response['Faces']
        elif status == 'FAILED':
            raise Exception(f"Face detection failed for Job ID: {job_id}")
        else:
            print(f"Face detection still in progress for Job ID: {job_id}... waiting")
            time.sleep(5)  # Wait before retrying

def blur_faces_in_video(faces, input_video, output_video):
    """Blur faces in video frames using OpenCV and Rekognition bounding boxes"""
    video = cv2.VideoCapture(input_video)
    output = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc(*'mp4v'), 30.0, 
                             (int(video.get(3)), int(video.get(4))))

    while True:
        ret, frame = video.read()
        if not ret:
            break

        frame_height, frame_width = frame.shape[:2]

        for faceT in faces:
            print(faceT)
            face = faceT['Face']
            bbox = face['BoundingBox']

            # Convert bounding box coordinates to pixel values
            left = int(bbox['Left'] * frame_width)
            top = int(bbox['Top'] * frame_height)
            width = int(bbox['Width'] * frame_width)
            height = int(bbox['Height'] * frame_height)

            # Extract face region
            face_region = frame[top:top+height, left:left+width]
            print('face_region - ')
            print(face_region)
            if not face_region:
                continue

            # Apply Gaussian blur to the face region
            blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)

            # Replace the face region with the blurred face
            frame[top:top+height, left:left+width] = blurred_face

        # Write the frame to the output video
        output.write(frame)

    video.release()
    output.release()
    print(f"Video processed and saved to {output_video}")

def lambda_handler(event, context):
    """Lambda handler triggered by S3 or SNS event"""
    
    # Extract video details from the event (assuming S3 event)
    s3_bucket = 'project-videostore'
    s3_video_key = 'people2.mp4'
    
    # Extract the Rekognition Job ID from the event
    rekognition_job_id = '9d18da03168822b67e29abbe95391bedd9d166626b78d1f6d2a615b7cea32a20'

    # Paths for downloading and processing
    local_input_video = '/tmp/input_video.mp4'
    local_output_video = '/tmp/output_video.mp4'

    # 1. Download video from S3 to /tmp/
    print('Download init')
    download_video_from_s3(s3_bucket, s3_video_key, local_input_video)
    print('Download done')

    # 2. Get face detection results using the Job ID from Rekognition
    print('Getting Job results')
    faces = get_face_detection_results(rekognition_job_id)
    print('results fetched')
    print(faces)

    # 3. Process video with OpenCV to blur detected faces
    print('blur start')
    blur_faces_in_video(faces, local_input_video, local_output_video)
    print('blur end')

    # 4. Upload blurred video back to S3
    upload_video_to_s3(local_output_video, s3_bucket, 'blurred-' + s3_video_key)

    return {
        'statusCode': 200,
        'body': 'Video processed successfully.'
    }
