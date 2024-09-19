# Use the official Ubuntu base image
FROM ubuntu:20.04

# Install Python and necessary system dependencies for OpenCV and FFmpeg
RUN apt-get update && \
    apt-get install -y python3 python3-pip \
    libjpeg-turbo8-dev \
    libpng-dev \
    libtiff-dev \
    libdc1394-22-dev \
    libx264-dev \
    ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install the Python dependencies
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy helper functions
COPY video_processor.py video_processor.py

# Copy handler function
COPY app.py .

# Specify the command to run the application
CMD ["python3", "app.py"]
