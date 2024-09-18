FROM public.ecr.aws/lambda/python:3.8
# Install the function's dependencies
# Copy file requirements.txt from your project folder and install
# the requirements in the app directory.

# Install EPEL and FFmpeg
RUN yum -y install amazon-linux-extras && \
    amazon-linux-extras install epel -y && \
    yum -y install ffmpeg && \
    yum clean all

COPY requirements.txt  .
RUN  pip install -r requirements.txt

# Copy helper functions
COPY video_processor.py video_processor.py

# Copy handler function (from the local app directory)
COPY  app.py  .

# Overwrite the command by providing a different command directly in the template.
CMD ["app.lambda_function"]