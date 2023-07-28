# Use the official Python image as the base image
FROM python:3.8

# Set environment variables (optional)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install the required dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project directory into the container
COPY . /app/

# Expose the port on which the Django development server will run (usually 8000)
EXPOSE 8000

# Start the Django development server when the container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
