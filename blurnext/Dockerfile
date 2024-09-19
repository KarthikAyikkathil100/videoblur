FROM public.ecr.aws/lambda/python:3.9

# Install Miniconda
RUN yum -y install bzip2 && \
    curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    /opt/conda/bin/conda clean -ya

# Add conda to the PATH
ENV PATH=/opt/conda/bin:$PATH

# Install OpenCV from conda-forge
RUN conda install -c conda-forge opencv

# Copy requirements.txt and install other Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy helper functions
COPY video_processor.py video_processor.py

# Copy handler function (from the local app directory)
COPY app.py .

# Overwrite the command by providing a different command directly in the template.
CMD ["app.lambda_function"]
