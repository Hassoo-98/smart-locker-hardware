# Smart Locker Hardware System 🛡️📷

Raspberry Pi 4 based smart locker controller with camera integration, Docker deployment, automatic GitHub updates, and production-ready scaling design.

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi%204-Model%20B-red?logo=raspberrypi)](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](#github-actions-pipeline)

## ✨ Features

- GPIO-based locker solenoid / relay control  
- Raspberry Pi Camera capture (photos + video streams)  
- Secure communication with Django backend via REST API  
- Fully containerized with **Docker & docker-compose**  
- Automatic code & image updates on boot  
- Multi-architecture Docker images (ARM64 / AMD64)  
- Designed for **100+ device** fleet management  
- Easy bulk provisioning via master SD card image + unique `.env`

## 📦 Architecture Overview
┌───────────────────────┐       ┌───────────────────────┐
│   Raspberry Pi 4      │       │   Django Backend      │
│                       │       │                       │
│  ┌───────────────┐    │       │  ┌─────────────────┐  │
│  │ camera_service│◄───┼───────┼─►│   API Endpoints │  │
│  └───────────────┘    │  HTTP │  └─────────────────┘  │
│  ┌───────────────┐    │       │                       │
│  │locker_controller◄───┼───────┼─►│   Device Status │  │
│  └───────────────┘    │       │  └─────────────────┘  │
│        │              │       └───────────────────────┘
│   GPIO pins           │
│   Pi Camera           │
└───────────────────────┘
▲
│ pull / update
│
GitHub + Docker Hub
text## 🚀 Quick Start

### 1. Prerequisites

```bash
# Update and install essentials
sudo apt update && sudo apt upgrade -y
sudo apt install -y git docker.io docker-compose

# Add current user to docker group (recommended: user 'pi')
sudo usermod -aG docker $USER
# Log out and back in (or reboot)
2. Clone & Configure
Bashgit clone https://github.com/yourusername/smart-locker-hardware.git
cd smart-locker-hardware

# Create and edit .env file
cp .env.example .env
nano .env
.env example:
ini# Required
API_URL=https://yourserver.com/api
API_TOKEN=dev_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEVICE_ID=locker-042

# Optional / advanced
LOG_LEVEL=INFO
CAMERA_RESOLUTION=1920x1080
HEARTBEAT_INTERVAL=30
3. Docker Deployment (recommended)
Bash# Build containers (first time ~5-10 min)
docker compose build

# Start in background
docker compose up -d

# Follow logs (most useful during setup)
docker compose logs -f camera
docker compose logs -f locker
🔄 Auto-update on Boot
The system uses a systemd service that runs start.sh → update.sh on every boot.
Bash# Install systemd service (one-time)
sudo cp locker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable locker.service
sudo systemctl start locker.service

# Check status
sudo systemctl status locker.service
What happens on boot:

update.sh → git pull latest code
Rebuilds containers if needed (docker compose build --pull)
Restarts services (docker compose up -d)

🏭 Scaling to 100+ Devices
AspectSolution / RecommendationUnique identificationUnique DEVICE_ID in each .envCode distributionSingle GitHub repo + auto-pull on bootContainer updatesDocker Hub + GitHub Actions multi-arch buildsFully automaticAdd Watchtower containerCentralized loggingELK / Loki / Graylog / Fluent Bit → central serverMonitoringPrometheus + Node Exporter + Grafana (lightweight on Pi)Mass provisioningBurn master SD card image → customize only .env per device
📂 Project Structure
textsmart-locker-hardware/
├── hardware/                    # Main application logic
│   ├── camera_service.py
│   └── locker_controller.py
├── scripts/                     # Boot & update logic
│   ├── start.sh
│   └── update.sh
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── locker.service               # systemd unit file
└── README.md
🔧 Development Tips

Use docker compose up (without -d) during development
Mount local code for fast iteration:

YAML# in docker-compose.yml (dev override)
volumes:
  - ./hardware:/app/hardware:ro
📜 License
MIT License
Feel free to use, modify, and deploy — just keep the spirit of open-source alive! 🚀
