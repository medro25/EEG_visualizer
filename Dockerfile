# Use the official Python image as a base
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    curl \
    libpugixml1v5 \
    && rm -rf /var/lib/apt/lists/*

# Install liblsl
RUN curl --retry 5 --retry-connrefused -L -o /tmp/liblsl-1.16.2-focal_amd64.deb \
    https://github.com/sccn/liblsl/releases/download/v1.16.2/liblsl-1.16.2-focal_amd64.deb && \
    dpkg -i /tmp/liblsl-1.16.2-focal_amd64.deb && \
    rm /tmp/liblsl-1.16.2-focal_amd64.deb

# Install mne-lsl via pip
RUN pip install mne-lsl

# Copy the Python requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .
# Expose the WebSocket port
EXPOSE 8765
# Set the default command to run the Python app
CMD ["python", "app.py"]
