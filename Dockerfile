# Use a base image with Python and Chrome pre-installed
# This image is based on Ubuntu and includes Chrome and chromedriver
FROM selenium/standalone-chrome:latest

# Set the working directory in the container
WORKDIR /app

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables for undetected-chromedriver
ENV PATH="/usr/bin/google-chrome:${PATH}"
ENV CHROME_PATH="/usr/bin/google-chrome"

# Command to run the application
# This assumes your main script is CWT_CLI/main.py
CMD ["python3", "CWT_CLI/main.py"]
