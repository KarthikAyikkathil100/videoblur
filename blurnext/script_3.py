import cv2
import face_recognition

# Open the video file
input_video_path = 'den_part.mp4'  # Change to your input video file
output_video_path = 's3_den_part_2.mp4'  # Output video file
cap = cv2.VideoCapture(input_video_path)

# Get the video properties
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 files
out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
scale_factor = 2
try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        resized_frame = cv2.resize(frame, (width * scale_factor, height * scale_factor))
        
        # Convert the image from BGR (OpenCV format) to RGB (face_recognition format)
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        
        # Find all face locations in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)

        # Blur each face found
        for (top, right, bottom, left) in face_locations:
            # Extract the face region
            face_region = frame[top:bottom, left:right]
            # Apply Gaussian blur to the face region
            blurred_face = cv2.GaussianBlur(face_region, (99, 99), 30)
            # Replace the original face region with the blurred version
            frame[top:bottom, left:right] = blurred_face

        # Write the processed frame to the output video
        og_frame = cv2.resize(frame, (width, height))
        out.write(og_frame)

        # Optional: Display the frame (comment out if not needed)
        cv2.imshow('Video', og_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except Exception as e:
    print(e)
# Release everything
cap.release()
out.release()
cv2.destroyAllWindows()
