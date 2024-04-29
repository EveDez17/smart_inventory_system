# Set the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /code

# Install system dependencies (if necessary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpython3-dev \
    musl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for the logs
RUN mkdir -p /code/logs

# Copy the requirements file and install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the project files into the container
COPY . /code/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "your_project_name.wsgi:application"]


