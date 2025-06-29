#!/bin/bash

set -euo pipefail

log() { echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $*"; }

install_stuff() {
    log "Updating system packages..."
    sudo apt-get update -y
    sudo apt-get upgrade -y

    log "Installing required packages..."
    sudo apt-get install -y python3 
    sudo apt-get install -y python3-pip 
    sudo apt-get install -y python3-venv 
    sudo apt-get install -y ffmpeg 
    sudo apt-get install -y wget 
    sudo apt-get install -y curl 
    sudo apt-get install -y zip 
    sudo apt-get install -y unzip 
    sudo apt-get install -y nginx 
    sudo apt-get install -y docker.io

    log "Installing Certbot..."
    sudo apt-get install -y certbot 
    sudo apt-get install -y python3-certbot-nginx

    log "Enabling and starting Docker and Nginx..."
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo systemctl enable nginx
    sudo systemctl start nginx

    log "Adding ubuntu user to docker group..."
    sudo usermod -aG docker ubuntu

    log "Docker and Nginx services are enabled and started."
    log "Installation complete. You can now configure your services."
    log "For Docker, you may want to log out and back in for group changes to take effect."
    log "For Nginx, you can find the configuration files in /etc/nginx/nginx.conf and /etc/nginx/sites-available/"
}

docker_app_setup() {
    log "Pulling latest Audio-Curl-Bot Docker image..."
    sudo docker pull rrumsey95/audio-curl-bot:latest
    
    if [[ $? -ne 0 ]]; then
        log "Failed to pull Docker image. Please check your Docker setup."
        exit 1
    fi

    log "Starting Audio-Curl-Bot container..."
    sudo docker run -d --name audio-curl-bot --restart unless-stopped --env-file /home/ubuntu/.env rrumsey95/audio-curl-bot:latest

    log "Docker application setup complete."
}

# Main
if [[ $EUID -ne 0 ]]; then
    log "Please run as root or with sudo."
    exit 1
fi

install_stuff
docker_app_setup
log "All setup tasks completed successfully."