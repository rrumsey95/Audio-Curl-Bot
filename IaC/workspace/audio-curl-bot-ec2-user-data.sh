#!/bin/bash

set -euo pipefail

log() { echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $*"; }

# Fetch .env and cookies.txt from AWS Secrets Manager and write to files
write_files() {
    log "Writing .env file..."
    if [[ -z "${env_file}" ]]; then
        log "Error: env_file is empty. Please check your AWS Secrets Manager configuration."
        exit 1
    fi
    echo "${env_file}" > /home/ubuntu/.env
    echo "YTDLP_COOKIES=/home/ubuntu/cookies.txt" >> /home/ubuntu/.env # add path to cookies.txt to .env file
    chmod 600 /home/ubuntu/.env
    chown ubuntu:ubuntu /home/ubuntu/.env
    if [[ $? -ne 0 ]]; then
        log "Failed to write .env file. Please check permissions."
        exit 1
    fi
    log ".env file written successfully."

    log "Writing cookies.txt file..."
    if [[ -z "${cookies_file}" ]]; then
        log "Error: cookies_file is empty. Please check your AWS Secrets Manager configuration."
        exit 1
    fi
    echo "${cookies_file}" > /home/ubuntu/cookies.txt
    chmod 600 /home/ubuntu/cookies.txt
    chown ubuntu:ubuntu /home/ubuntu/cookies.txt
    if [[ $? -ne 0 ]]; then
        log "Failed to write cookies.txt file. Please check permissions."
        exit 1
    fi
    log "cookies.txt file written successfully."
}

install_stuff() {
    log "Updating system packages..."
    sudo apt-get update -y
    sudo apt-get upgrade -y

    log "Installing required packages..."
    sudo apt-get install -y python3 
    sudo apt-get install -y python3-full
    sudo apt-get install -y python3-dev
    sudo apt-get install -y python3-pip 
    sudo apt-get install -y python3-venv
    sudo apt-get install -y pipx 
    sudo apt-get install -y build-essential 
    sudo apt-get install -y ffmpeg 
    sudo apt-get install -y wget 
    sudo apt-get install -y curl 
    sudo apt-get install -y zip 
    sudo apt-get install -y unzip 
    sudo apt-get install -y nginx 
    sudo apt-get install -y docker.io
    sudo apt-get install -y docker-compose
    sudo apt-get install -y git
    sudo apt-get install -y software-properties-common 

    sudo apt install -y libffi-dev 
    sudo apt install -y libnacl-dev 
    sudo apt install -y libssl-dev
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt install python3.8 python3.8-dev python3.8-venv python3-pip -y

    log "Installing Certbot..."
    sudo apt-get install -y certbot 
    sudo apt-get install -y python3-certbot-nginx

    log "Enabling and starting Docker and Nginx..."
    sudo systemctl enable docker
    sudo systemctl start docker
    # sudo systemctl enable nginx
    # sudo systemctl start nginx

    log "Adding ubuntu user to docker group..."
    sudo usermod -aG docker ubuntu

    log "Docker and Nginx services are enabled and started."
    log "Installation complete. You can now configure your services."
    log "For Docker, you may want to log out and back in for group changes to take effect."
    log "For Nginx, you can find the configuration files in /etc/nginx/nginx.conf and /etc/nginx/sites-available/"
}

docker_app_setup() {
    log "Pulling latest Audio-Curl-Bot Docker image..."
    docker pull rrumsey95/audio-curl-bot:latest
    
    if [[ $? -ne 0 ]]; then
        log "Failed to pull Docker image. Please check your Docker setup."
        exit 1
    fi

    log "Starting Audio-Curl-Bot container..."
    docker run -d --name audio-curl-bot --restart unless-stopped --env-file /home/ubuntu/.env rrumsey95/audio-curl-bot:latest

    log "Docker application setup complete."
}

running_stuff_locally() {
    git clone https://github.com/rrumsey95/Audio-Curl-Bot.git
    python3 -m venv venv
    python3 -m venv .venv
    source venv/bin/activate
    source .venv/bin/activate
    log "Installing Python dependencies..."
    python3 -m pip install -r /home/ubuntu/Audio-Curl-Bot/requirements.txt
    pip install -U discord.py
    pip install -U "discord.py[voice]"
    pip install -U PyNaCl
    pipx install yt_dlp
    pip install -U asyncio
    pip install -U dotenv
    log "Python dependencies installed."
    log "Making sure the python files are executable..."
    chmod +x /home/ubuntu/Audio-Curl-Bot/src/Audio-Curl-Bot.py
    chmod +x /home/ubuntu/Audio-Curl-Bot/src/bot/__init__.py 
    chmod +x /home/ubuntu/Audio-Curl-Bot/src/bot/commands.py  
    chmod +x /home/ubuntu/Audio-Curl-Bot/src/bot/core.py  
    chmod +x /home/ubuntu/Audio-Curl-Bot/src/bot/queue.py
    log "Starting the bot..."
    python3 /home/ubuntu/Audio-Curl-Bot/src/Audio-Curl-Bot.py
}

# Main
if [[ $EUID -ne 0 ]]; then
    log "Please run as root or with sudo."
    exit 1
fi

install_stuff
docker_app_setup
# running_stuff_locally
log "All setup tasks completed successfully."