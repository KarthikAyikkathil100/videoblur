FROM public.ecr.aws/lambda/python:3.9

# Install necessary system dependencies for OpenCV and other libraries
RUN yum -y install curl && \
    curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    /opt/conda/bin/conda clean -afy

# Add Conda to the PATH
ENV PATH=/opt/conda/bin:$PATH

# # Update Conda
# RUN conda update -n base -c defaults conda -y

# # Create environment and install pip
# RUN conda create -n envname python=3.9 anaconda -y && \
#     conda install -n envname pip -y

# Update Conda and create environment with pip
RUN conda update -n base -c defaults conda -y && \
    conda create -n envname python=3.9 && \
    conda install -n envname pip -y

# Update Conda and create environment with pip
# RUN conda create -n envname python=3.9 anaconda -y && \
#     conda install -n envname pip -y

# Copy requirements.txt and install dependencies
COPY requirements.txt .
# RUN conda run -n envname pip install -r requirements.txt

# # Install OpenCV in the conda environment
# RUN conda run -n envname conda install -c conda-forge opencv -y
RUN conda run -n envname pip install -r requirements.txt && \
    conda run -n envname conda install -c conda-forge opencv -y


# Copy helper functions and handler function
COPY video_processor.py .
COPY app.py .

# Overwrite the command by providing a different command directly in the template.
CMD ["app.lambda_function"]
