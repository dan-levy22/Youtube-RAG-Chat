# --------- Stage 1: "Base" ----------
FROM python:3.12-slim as base

WORKDIR /code

# Set env vars for clean logs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install uv
RUN pip install uv

# Copy only the requirements file first to leverage Docker's layer caching
COPY ./frontend/requirements.txt /code/requirements.txt

RUN uv pip install --no-cache-dir --system -r requirements.txt


# --------- Stage 2: "Production" ----------
# Installs all dependencies needed for local dev and for testing
# By inheriting from 'base', we already have Python, uv, and all dependencies installed.
FROM base as production

# Copy only the frontend application code into the image.
COPY ./frontend /code/frontend
COPY ./config /code/config
COPY ./shared /code/shared

EXPOSE 8501

#  The default CMD for this stage is for local development
CMD ["streamlit", "run", "frontend/frontend.py"]


# ----------------- Stage 3: Development ----------------
FROM base as development 

# Note: relevant code is accessed through volumes in docker-compose 

# Command to run the streamlit app
CMD ["streamlit", "run", "frontend/frontend.py"]

# ------------- OLD VERSION ------------------

# # Use an official Python runtime as a parent image
# FROM python:3.12-slim

# # Set the working directory in the container
# WORKDIR /code

# # [Optimisation] Install uv itself first.
# # This step will be cached and run only once
# RUN pip install uv

# # Copy the requirements file
# COPY requirements.txt .

# # Install dependencies
# RUN uv pip install --no-cache --system -r requirements.txt

# # Copy the rest of your application's code
# COPY . .

# # Expose the port Streamlit runs on
# EXPOSE 8501

# # Command to run the streamlit app
# CMD ["streamlit", "run", "frontend/frontend.py"]