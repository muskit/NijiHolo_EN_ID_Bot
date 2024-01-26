FROM ubuntu:latest

# Install dependencies
RUN apt update && apt upgrade -y
RUN apt install -y python3 python3-pip chromium-browser chromium-chromedriver git

# Set working directory
WORKDIR /app

# Install pip dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Mount working directory
VOLUME ./run

# Copy source code
COPY . .

# Run the bot
CMD ["python3", "src/main.py"]