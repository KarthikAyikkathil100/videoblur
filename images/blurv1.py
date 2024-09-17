import cv2
import os


# Define the path to the Haar cascade XML file
haar_cascade_path = os.path.join(os.path.dirname(__file__), 'cascades', 'haarcascade_frontalface_default.xml')

# Initialize the face cascade
face_cascade = cv2.CascadeClassifier(haar_cascade_path)

if face_cascade.empty():
    raise Exception(f"Failed to load cascade classifier from {haar_cascade_path}")

print(f"Cascade classifier loaded from {haar_cascade_path}")

def download_video_from_s3(bucket, video_key, download_path):
    """Download video from S3 to /tmp/"""
    s3.download_file(bucket, video_key, download_path)
    print(f"Video downloaded from S3: {video_key}")

def upload_video_to_s3(local_file, bucket, output_key):
    """Upload video to S3 from /tmp/"""
    s3.upload_file(local_file, bucket, output_key)
    print(f"Blurred video uploaded to S3: {output_key}")

def blur_faces_in_video(input_video, output_video):
    """Blur faces in video frames using OpenCV and local face detection"""
    # Load the pre-trained Haar Cascade classifier -- This is already initialized 
    # face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    video = cv2.VideoCapture(input_video)
    output = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc(*'mp4v'), 30.0, 
                             (int(video.get(3)), int(video.get(4))))

    while True:
        ret, frame = video.read()
        if not ret:
            break

        frame_height, frame_width = frame.shape[:2]

        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            # Extract face region
            face_region = frame[y:y+h, x:x+w]
            if len(face_region) == 0:
                continue

            # Apply Gaussian blur to the face region
            blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)

            # Replace the face region with the blurred face
            frame[y:y+h, x:x+w] = blurred_face

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
