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


def apply_faces_to_video(final_timestamps, local_path_to_video, local_output, video_metadata, upper_bound_calc, color=(255, 0, 0), thickness=2):
    print('Using below for upper bound calculation')
    print(upper_bound_calc)
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
    
    # Open the video
    while v.isOpened():
        has_frame, frame = v.read()
        if has_frame:
            for t in final_timestamps:
                faces = final_timestamps.get(t)
                lower_bound = int(int(t) / 1000 * frame_rate)
                upper_bound = int(int(t) / 1000 * frame_rate + frame_rate / upper_bound_calc) + 1
                # upper_bound = int(int(t) / 1000 * frame_rate + frame_rate) + 1

                print('lower_bound -')
                print(lower_bound)
                print('upper_bound -')
                print(upper_bound)
                print('-----------------------')

                if (frame_counter >= lower_bound) and (frame_counter <= upper_bound):
                    for f in faces:
                        x = int(f['Left'] * frame_width) - width_delta
                        y = int(f['Top'] * frame_height) - height_delta
                        w = int(f['Width'] * frame_width) + 2 * width_delta
                        h = int(f['Height'] * frame_height) + 2 * height_delta

                        x1, y1 = x, y
                        x2, y2 = x1 + w, y1 + h

                        to_blur = frame[y1:y2, x1:x2]
                        blurred = anonymize_face_pixelate(to_blur, blocks=10)
                        frame[y1:y2, x1:x2] = blurred

                        # frame = cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)

            out.write(frame)
            frame_counter += 1
        else:
            break

    out.release()
    v.release()
    print(f"Complete. {frame_counter} frames were written.")

def apply_faces_to_video_v3(final_timestamps, local_path_to_video, local_output, video_metadata, upper_bound_calc, color=(255, 0, 0), thickness=2):
    print('Using below for upper bound calculation')
    print(upper_bound_calc)
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
    
    # Open the video
    while v.isOpened():
        has_frame, frame = v.read()
        if has_frame:
            for t in final_timestamps:
                faces = final_timestamps.get(t)
                lower_bound = int(int(t) / 1000 * frame_rate)
                upper_bound = int(int(t) / 1000 * frame_rate + frame_rate / upper_bound_calc) + 1
                # upper_bound = int(int(t) / 1000 * frame_rate + frame_rate) + 1

                print('lower_bound -')
                print(lower_bound)
                print('upper_bound -')
                print(upper_bound)
                print('-----------------------')

                if (frame_counter >= lower_bound) and (frame_counter <= upper_bound):
                    for f in faces:
                        x = int(f['Left'] * frame_width) - width_delta
                        y = int(f['Top'] * frame_height) - height_delta
                        w = int(f['Width'] * frame_width) + 2 * width_delta
                        h = int(f['Height'] * frame_height) + 2 * height_delta

                        x1, y1 = x, y
                        x2, y2 = x1 + w, y1 + h

                        to_blur = frame[y1:y2, x1:x2]
                        blurred = anonymize_face_pixelate(to_blur, blocks=10)
                        frame[y1:y2, x1:x2] = blurred

                        # frame = cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)

            # out.write(frame)
            frame_counter += 1

            # Optinally processing next frame
            current_frame = frame_counter-1
            has_next_frame, next_frame = v.read()
            if has_next_frame:
                # Process the next frame
                for t in final_timestamps:
                    faces = final_timestamps.get(t)
                    lower_bound = int(int(t) / 1000 * frame_rate)
                    upper_bound = int(int(t) / 1000 * frame_rate + frame_rate / upper_bound_calc) + 1
                    # upper_bound = int(int(t) / 1000 * frame_rate + frame_rate) + 1

                    print('lower_bound -')
                    print(lower_bound)
                    print('upper_bound -')
                    print(upper_bound)
                    print('-----------------------')

                    if (frame_counter >= lower_bound) and (frame_counter <= upper_bound):
                        for f in faces:
                            x = int(f['Left'] * frame_width) - width_delta
                            y = int(f['Top'] * frame_height) - height_delta
                            w = int(f['Width'] * frame_width) + 2 * width_delta
                            h = int(f['Height'] * frame_height) + 2 * height_delta

                            x1, y1 = x, y
                            x2, y2 = x1 + w, y1 + h

                            to_blur = frame[y1:y2, x1:x2]
                            blurred = anonymize_face_pixelate(to_blur, blocks=10)
                            frame[y1:y2, x1:x2] = blurred #Overwrite on the orignal frame
            
                # Get back to the orignal frame
                v.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
                out.write(frame)
            else:
                out.write(frame)
        else:
            break

    out.release()
    v.release()
    print(f"Complete. {frame_counter} frames were written.")

def apply_faces_to_video_v4(final_timestamps, local_path_to_video, local_output, video_metadata, upper_bound_calc, next_blurs, color=(255, 0, 0), thickness=2):
    print('Using below for upper bound calculation')
    print(upper_bound_calc)
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
    
    # Open the video
    while v.isOpened():
        has_frame, frame = v.read()
        if has_frame:
            for t in final_timestamps:
                faces = final_timestamps.get(t)
                lower_bound = int(int(t) / 1000 * frame_rate)
                upper_bound = int(int(t) / 1000 * frame_rate + frame_rate / upper_bound_calc) + 1
                # upper_bound = int(int(t) / 1000 * frame_rate + frame_rate) + 1

                print('lower_bound -')
                print(lower_bound)
                print('upper_bound -')
                print(upper_bound)
                print('-----------------------')

                if (frame_counter >= lower_bound) and (frame_counter <= upper_bound):
                    for f in faces:
                        x = int(f['Left'] * frame_width) - width_delta
                        y = int(f['Top'] * frame_height) - height_delta
                        w = int(f['Width'] * frame_width) + 2 * width_delta
                        h = int(f['Height'] * frame_height) + 2 * height_delta

                        x1, y1 = x, y
                        x2, y2 = x1 + w, y1 + h

                        to_blur = frame[y1:y2, x1:x2]
                        blurred = anonymize_face_pixelate(to_blur, blocks=10)
                        frame[y1:y2, x1:x2] = blurred

                        # frame = cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)

                # out.write(frame)
                print('block 1')
                frame_counter += 1
                print('Calling the nextBlur fn')
                blur_next_frames(next_blurs, frame, v, (frame_counter-1), final_timestamps, local_path_to_video, local_output, video_metadata, upper_bound_calc, color=(255, 0, 0), thickness=2)
                v.set(cv2.CAP_PROP_POS_FRAMES, (frame_counter-1))
                out.write(frame)
        else:
            break

    out.release()
    v.release()
    print(f"Complete. {frame_counter} frames were written.")


def blur_next_frames(blur_next_n_frames, og_frame, v, og_frame_count, final_timestamps, local_path_to_video, local_output, video_metadata, upper_bound_calc, color=(255, 0, 0), thickness=2):
    for i in range(1, blur_next_n_frames+1):
        current_frame = og_frame_count+1
        has_next_frame, next_frame = v.read()
        if has_next_frame:
            # Process the next frame
            for t in final_timestamps:
                faces = final_timestamps.get(t)
                lower_bound = int(int(t) / 1000 * frame_rate)
                upper_bound = int(int(t) / 1000 * frame_rate + frame_rate / upper_bound_calc) + 1
                # upper_bound = int(int(t) / 1000 * frame_rate + frame_rate) + 1

                print('lower_bound -')
                print(lower_bound)
                print('upper_bound -')
                print(upper_bound)
                print('-----------------------')

                if (og_frame_count >= lower_bound) and (og_frame_count <= upper_bound):
                    for f in faces:
                        x = int(f['Left'] * frame_width) - width_delta
                        y = int(f['Top'] * frame_height) - height_delta
                        w = int(f['Width'] * frame_width) + 2 * width_delta
                        h = int(f['Height'] * frame_height) + 2 * height_delta

                        x1, y1 = x, y
                        x2, y2 = x1 + w, y1 + h

                        to_blur = og_frame[y1:y2, x1:x2]
                        blurred = anonymize_face_pixelate(to_blur, blocks=10)
                        og_frame[y1:y2, x1:x2] = blurred #Overwrite on the orignal frame        
                        
            # Get back to the orignal frame
            # v.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            # out.write(frame)
        # else:
        #     out.write(frame)
        

def apply_faces_to_video_test(final_timestamps, local_path_to_video, local_output, video_metadata, color=(255, 0, 0), thickness=2):
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
    
    # Open the video
    while v.isOpened():
        has_frame, frame = v.read()
        if has_frame:
            for t in final_timestamps:
                faces = final_timestamps.get(t)
                lower_bound = int(int(t) / 1000 * frame_rate)
                # upper_bound = int(int(t) / 1000 * frame_rate + frame_rate / 2) + 1
                upper_bound = int(int(t) / 1000 * frame_rate + frame_rate) + 1

                if (True):
                    for f in faces:
                        x = int(f['Left'] * frame_width) - width_delta
                        y = int(f['Top'] * frame_height) - height_delta
                        w = int(f['Width'] * frame_width) + 2 * width_delta
                        h = int(f['Height'] * frame_height) + 2 * height_delta

                        x1, y1 = x, y
                        x2, y2 = x1 + w, y1 + h

                        to_blur = frame[y1:y2, x1:x2]
                        blurred = anonymize_face_pixelate(to_blur, blocks=10)
                        frame[y1:y2, x1:x2] = blurred

                        frame = cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)

            out.write(frame)
            frame_counter += 1
        else:
            break

    out.release()
    v.release()
    print(f"Complete. {frame_counter} frames were written.")


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