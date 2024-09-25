import cv2
import numpy as np
from moviepy.editor import *
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import os
from collections import deque


def anonymize_face_pixelate(image, blocks=30):
    """
    Computes a pixelated blur with OpenCV
    Args:
        image (ndarray): The image to be blurred
        blocks (int): Number of pixel blocks (default is 10)
    Returns:
        image (ndarray): The blurred image
    """
    # divide the input image into NxN blocks
    (h, w) = image.shape[:2]
    x_coordinates, y_coordinates = np.linspace(0, w, blocks + 1, dtype="int"), np.linspace(0, h, blocks + 1, dtype="int")
    
    # loop over the blocks along x and y axis
    for i in range(1, len(y_coordinates)):
        for j in range(1, len(x_coordinates)):
            # compute the first and last (x, y)-coordinates for the current block
            first_x, last_x = x_coordinates[j - 1], x_coordinates[j]
            first_y, last_y = y_coordinates[i - 1], y_coordinates[i]
            # extract the ROI
            roi = image[first_y:last_y, first_x:last_x]
            # compute the mean of the ROI 
            (b, g, r) = [int(x) for x in cv2.mean(roi)[:3]]
            # draw a rectangle with the mean RGB values over the ROI in the original image
            cv2.rectangle(image, (first_x, first_y), (last_x, last_y), (b, g, r), -1)

    # return the pixelated blurred image
    return image


def apply_faces_to_video(final_timestamps, local_path_to_video, local_output, video_metadata, color=(255,0,0), thickness=2):
    # Extract video info
    frame_rate = video_metadata["FrameRate"]
    frame_height = video_metadata["FrameHeight"]
    frame_width = video_metadata["FrameWidth"]
    width_delta = int(frame_width / 250)
    height_delta = int(frame_height / 100)
    # Set up support for OpenCV
    frame_counter = 0
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    # Create the file pointers
    v = cv2.VideoCapture(local_path_to_video)
    print("VideoCapture - local path to video")
    out = cv2.VideoWriter(
        filename=local_output,
        fourcc=fourcc,
        fps=int(frame_rate),
        frameSize=(frame_width, frame_height)
    )

    # Parameters
    sliding_window_size = 3  # Number of frames to apply the blur

    # Initialize frame counter
    frame_counter = 0

    while v.isOpened():
        has_frame, frame = v.read()
        if not has_frame:
            break

        blurred_this_frame = False
        frame_queue = deque(maxlen=sliding_window_size)
        frame_queue.append(frame.copy())  # Store a copy of the current frame

        # Reset the current frame for blurring
        current_frame_blurred = frame.copy()

        for t in final_timestamps:
            faces = final_timestamps.get(t, [])
            lower_bound = int(int(t) / 1000 * original_frame_rate)
            upper_bound = int(int(t) / 1000 * original_frame_rate + original_frame_rate / 2) + 1
            
            if lower_bound <= frame_counter <= upper_bound:
                for f in faces:
                    # Calculate bounding box
                    x = int(f['Left'] * frame_width) - width_delta
                    y = int(f['Top'] * frame_height) - height_delta
                    w = int(f['Width'] * frame_width) + 2 * width_delta
                    h = int(f['Height'] * frame_height) + 2 * height_delta
                    
                    x1, y1 = max(x, 0), max(y, 0)
                    x2, y2 = min(x1 + w, frame_width), min(y1 + h, frame_height)

                    # Blur the region of interest in the current frame
                    to_blur = current_frame_blurred[y1:y2, x1:x2]
                    blurred = anonymize_face_pixelate(to_blur, blocks=10)
                    current_frame_blurred[y1:y2, x1:x2] = blurred

                    # Draw rectangle around the face
                    cv2.rectangle(current_frame_blurred, (x, y), (x + w, y + h), (255, 0, 0), 3)
                    blurred_this_frame = True

                    # Add the frame to the sliding window
                    frame_queue.append(current_frame_blurred.copy())

        # If blurring was done, write the blurred frame to the output
        if blurred_this_frame:
            out.write(current_frame_blurred)
        else:
            out.write(frame)  # Write the original frame if no blurring was done

        frame_counter += 1

    # Clean up
    v.release()
    out.release()


def integrate_audio(original_video, output_video, audio_path='/tmp/audio.mp3'):
    # Extract audio
    my_clip = VideoFileClip(original_video)
    my_clip.audio.write_audiofile(audio_path)
    temp_location = '/tmp/output_video.mp4'
    # Join output video with extracted audio
    videoclip = VideoFileClip(output_video)
    # new_audioclip = CompositeAudioClip([audioclip])
    # videoclip.audio = new_audioclip
    videoclip.write_videofile(temp_location, codec='libx264', audio=audio_path, audio_codec='libmp3lame')

    os.rename(temp_location, output_video)
    # Delete audio
    os.remove(audio_path)

    print('Complete')