FROM alpine:latest

# Install dependencies
RUN apk update && apk add --no-cache python3 py3-pip chromium chromium-chromedriver git

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