# FROM continuumio/miniconda3
# COPY environment.yml .
# RUN conda env create -f environment.yml
# RUN echo "source activate devenv" > ~/.bashrc
# CMD ["app.lambda_function"]


# Use the official Miniconda3 image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Copy the environment.yml file to the container
COPY environment.yml .

# Create the conda environment
RUN conda env create -f environment.yml

# Activate the environment and ensure it's the default
RUN echo "source activate devenv" > ~/.bashrc
ENV PATH /opt/conda/envs/devenv/bin:$PATH

# Copy your application code to the container
COPY . .

# Command to run your application (adjust as necessary)
CMD ["python", "-m", "app.lambda_function"]
