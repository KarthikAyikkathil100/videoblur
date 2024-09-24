FROM public.ecr.aws/lambda/python:3.9

# Install necessary system dependencies for OpenCV and other libraries
# RUN yum update -y && yum install -y wget && yum clean all
RUN yum update -y && yum install -y wget which ffmpeg && yum clean all

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh && sh Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda

# Add Conda to the PATH
# ENV PATH=/opt/conda/bin:$PATH

COPY environment.yml /tmp/environment.yml

RUN /opt/miniconda/bin/conda env create --file /tmp/environment.yml --prefix /opt/conda-env

RUN /opt/conda-env/bin/pip install awslambdaric

# We now replace the image’s existing Python with Python from the conda environment:
RUN mv /var/lang/bin/python3.9 /var/lang/bin/python3.9-clean && ln -sf /opt/conda-env/bin/python /var/lang/bin/python3.9
COPY app.py /opt/my-code/app.py
COPY video_processor.py /opt/my-code/video_processor.py
ENV PYTHONPATH "/var/lang/lib/python3.9/site-packages:/opt/my-code"

CMD ["app.lambda_function"]
