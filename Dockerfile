FROM alpine:latest

# Install dependencies
RUN apk update && apk add font-noto-cjk git build-base linux-headers python3 python3-dev py3-pip py3-opencv chromium chromium-chromedriver

# Set working directory
WORKDIR /app

# Create virtual environment
# RUN python3 -m venv .venv
# ENV PATH="/app/.venv/bin:$PATH"

# Install pip dependencies
COPY requirements.txt .
RUN pip3 install --break-system-packages -r requirements.txt

# Copy source code
COPY . .

# Mount persistent working directory
VOLUME ./run

# Run the bot
CMD ["python3", "-u", "src/main.py"]
