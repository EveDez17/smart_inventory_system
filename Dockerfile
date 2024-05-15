# Use an official lightweight Python image as the base image
FROM python:3.9-slim

# Prevent Python from writing pyc files to disk (optional)
ENV PYTHONDONTWRITEBYTECODE 1

# Prevent Python from buffering stdout and stderr (optional)
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for Python packages like psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && apt-get clean

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the Django project files into the container
COPY . /app/

# Collect static files; assumes STATICFILES_STORAGE is set to Cloudinary in settings
RUN python manage.py collectstatic --noinput

# Command to run the application server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "warehouse.wsgi:application"]





