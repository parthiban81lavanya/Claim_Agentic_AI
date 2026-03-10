# Use lightweight Python image
#FROM python:3.11-slim
FROM python:3.11

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
#C:\Anaconda\anaconda3\python.exe -m pip install --upgrade pip setuptools wheel
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app

# Expose Flask port
EXPOSE 5000

# Flask environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run Flask
CMD ["flask", "run"]

# # Base Python environment
# FROM python:3.10

# # Set working directory
# WORKDIR /app

# # Copy project files
# COPY . /app

# # Install dependencies
# RUN pip install --no-cache-dir -r requirements.txt

# # Expose Flask port
# EXPOSE 5000

# # Run application
# CMD ["python", "app.py"]