# --- Stage 1: "Base" ---
# Installs all dependencies needed for local dev and for testing.
FROM python:3.12-slim as base

WORKDIR /code

# Add the project's root directory inside the container to the PYTHONPATH.
# This ensures that all top-level modules (app, config, db, shared) can be found.
ENV PYTHONPATH=/code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install uv, the fast installer
RUN pip install uv

# For a test stage, you'd typically have a separate requirements-dev.txt
# that includes pytest, etc. For now, we'll assume they are in requirements.txt
COPY app/requirements.txt /code/requirements.txt

RUN uv pip install --no-cache-dir --system -r requirements.txt


# --------------- Stage 2: "Production" ------------------
# This is the final, lean stage for deployment.
FROM base as production

# Copy your application code into the image.
COPY ./app /code/app
COPY ./config /code/config
COPY ./shared /code/shared
COPY ./db /code/db

EXPOSE 8000

# Set the command to run the app using the Gunicorn production server
# CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "-b", "0.0.0.0:8000"]

# Test using uvicorn first
CMD ["sh", "-c", "echo 'Waiting for secret initialization...'"; "sleep 15"; "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]


# --------------- Stage 3: Development ------------------
FROM base as development

# The default CMD for this stage is for local development
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]


# ------------- Stage 4: "Test"- linting addition needed -----------------
# This stage builds on the 'development' stage to run tests in a CI/CD pipeline.
FROM base as test

# Copy all the application and test code.
# The `development` stage doesn't do this because it uses volumes.
COPY ./app /code/app
COPY ./config /code/config
COPY ./shared /code/shared
COPY ./tests /code/tests 

# The command for this stage runs the test suite and then exits.
# Replace 'pytest' with your actual test command.
CMD ["pytest"]





# --------------- OLD VERSION ------------------

# FROM python:3.12-slim

# # Set a neutral working directory, so that 'app' is not the root directory
# WORKDIR /code

# # [Optimisation] Install uv itself first.
# # This step will be cached and run only once
# RUN pip install uv

# # Copy the requirements file into the container at /app
# COPY app/requirements.txt .

# # Install any needed packages specified in requirements.txt
# RUN uv pip install --no-cache --system -r requirements.txt

# # Copy the rest of the application's code from the host to the image filesystem
# COPY ./app /code/app
# COPY ./db /code/db

# # Tell python to add the '/app' directory to its path.
# # This ensures that imports like 'from app.database import ...' will work correctly.
# ENV PYTHONPATH=/app

# # Expose the port the app runs on
# EXPOSE 8000

# # Command to run the application
# # The host 0.0.0.0 allows the container to be accessible from outside the container
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]