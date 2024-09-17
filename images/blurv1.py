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

def detect_faces_in_image(image):
    """Detect faces in a single image using Rekognition"""
    _, buffer = cv2.imencode('.jpg', image)
    response = rekognition.detect_faces(
        Image={'Bytes': buffer.tobytes()},
        Attributes=['ALL']
    )
    return response['Faces']

def blur_faces_in_video(input_video, output_video):
    """Blur faces in video frames using OpenCV"""
    video = cv2.VideoCapture(input_video)
    output = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc(*'mp4v'), 30.0, 
                             (int(video.get(3)), int(video.get(4))))

    while True:
        ret, frame = video.read()
        if not ret:
            break
        
        faces = detect_faces_in_image(frame)

        frame_height, frame_width = frame.shape[:2]

        for faceT in faces:
            face = faceT['BoundingBox']

            # Convert bounding box coordinates to pixel values
            left = int(face['Left'] * frame_width)
            top = int(face['Top'] * frame_height)
            width = int(face['Width'] * frame_width)
            height = int(face['Height'] * frame_height)

            # Extract face region
            face_region = frame[top:top+height, left:left+width]
            if len(face_region) == 0:
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

    # Paths for downloading and processing
    local_input_video = '/tmp/input_video.mp4'
    local_output_video = '/tmp/output_video.mp4'

    # 1. Download video from S3 to /tmp/
    download_video_from_s3(s3_bucket, s3_video_key, local_input_video)

    # 2. Process video with OpenCV to blur detected faces
    blur_faces_in_video(local_input_video, local_output_video)

    # 3. Upload blurred video back to S3
    upload_video_to_s3(local_output_video, s3_bucket, 'blurred-' + s3_video_key)

    return {
        'statusCode': 200,
        'body': 'Video processed successfully.'
    }
