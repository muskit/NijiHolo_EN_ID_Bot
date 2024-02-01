FROM alpine:latest

# Install dependencies
RUN apk update && apk add git build-base linux-headers python3 python3-dev py3-pip chromium chromium-chromedriver

# Set working directory
WORKDIR /app

# Install pip dependencies
COPY requirements.txt .
RUN python3 -m venv .venv && source .venv/bin/activate
RUN pip3 install -r requirements.txt

# Copy source code
COPY . .

# Mount working directory
VOLUME ./run

# Run the bot
CMD ["python3", "src/main.py"]
