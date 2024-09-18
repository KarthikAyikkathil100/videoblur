FROM public.ecr.aws/lambda/python:3.8
# Install the function's dependencies
# Copy file requirements.txt from your project folder and install
# the requirements in the app directory.

# Install required system packages
RUN yum install -y curl tar && yum clean all

# Download and install FFmpeg
RUN curl -L https://github.com/FFmpeg/FFmpeg/releases/download/n5.1.2/ffmpeg-release-amd64-static.tar.xz -o /tmp/ffmpeg.tar.xz && \
    tar -xvf /tmp/ffmpeg.tar.xz -C /tmp && \
    cp /tmp/ffmpeg-*-static/ffmpeg /usr/bin/ && \
    cp /tmp/ffmpeg-*-static/ffprobe /usr/bin/ && \
    rm -rf /tmp/ffmpeg-* /tmp/ffmpeg.tar.xz

COPY requirements.txt  .
RUN  pip install -r requirements.txt

# Copy helper functions
COPY video_processor.py video_processor.py

# Copy handler function (from the local app directory)
COPY  app.py  .

# Overwrite the command by providing a different command directly in the template.
CMD ["app.lambda_function"]