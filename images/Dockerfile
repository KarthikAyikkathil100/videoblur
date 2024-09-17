# Use the official AWS Lambda Python 3.9 image
FROM public.ecr.aws/lambda/python:3.9

# Install necessary system dependencies for OpenCV
RUN yum -y install libjpeg-turbo libpng libtiff libdc1394 ffmpeg

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Lambda function code into the container
COPY . .

# Set the CMD to the Lambda function handler
CMD ["blurv1.lambda_handler"]
