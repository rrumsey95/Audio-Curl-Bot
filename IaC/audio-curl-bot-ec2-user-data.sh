#!/bin/bash

set -euo pipefail

log() { echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $*"; }

install_stuff() {
    log "Updating system packages..."
    sudo apt-get update -y
    sudo apt-get upgrade -y

    log "Installing required packages..."
    sudo apt-get install -y \
        python3 python3-pip python3-venv \
        ffmpeg \
        wget curl zip unzip \
        nginx docker.io

    log "Installing Certbot..."
    sudo apt-get install -y certbot python3-certbot-nginx

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

# Main
if [[ $EUID -ne 0 ]]; then
    log "Please run as root or with sudo."
    exit 1
fi

install_stuff