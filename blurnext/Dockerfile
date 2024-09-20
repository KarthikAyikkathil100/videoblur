# Use Amazon Linux 2 as the base image
FROM amazonlinux:2

# Install Miniconda
RUN yum install -y bzip2 && \
    curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh

# Set environment variables
ENV PATH=/opt/conda/bin:$PATH

# Create a new conda environment and install required libraries
RUN conda create -n myenv python=3.9 opencv ffmpeg numpy imageio pillow -y && \
    conda clean -afy

# Install pip in the conda environment
RUN conda install -n myenv pip -y

# Install MoviePy using pip
RUN /opt/conda/bin/pip install moviepy

# Install additional packages using pip from requirements.txt
COPY requirements.txt .
RUN /opt/conda/bin/pip install -r requirements.txt

# Copy your application code
COPY video_processor.py .
COPY app.py .

# Set the working directory
WORKDIR /app

# Set the entrypoint to use the conda environment and point to the Lambda handler
CMD ["bash", "-c", "source activate myenv && python -m awslambdaric app.lambda_function"]
