# Set the base image
FROM python:3.9-slim

# Set environment variables to prevent Python from writing pyc files to disk (optional)
ENV PYTHONDONTWRITEBYTECODE 1
# Set environment variables to ensure Python outputs are flushed to the terminal.
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the project files into the container
COPY . /code/

# Create and use a non-root user
RUN useradd -m myuser
USER myuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "warehouse.wsgi:application"]




