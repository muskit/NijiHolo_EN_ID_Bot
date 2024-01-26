FROM ubuntu:latest

# Install dependencies
RUN apt update && apt install -y python3 python3-pip chromium-browser chromium-chromedriver git

# Set working directory
WORKDIR /app

# Install pip dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy source code
COPY . .

# Mount working directory
VOLUME ./run

# Run the bot
CMD ["python3", "src/main.py"]