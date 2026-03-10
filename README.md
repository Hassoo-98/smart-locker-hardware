# Smart Locker Hardware System (Raspberry Pi 4)

## Overview

This repository contains the hardware software for the **Smart Locker system** running on Raspberry Pi 4. It is designed to:

- Control lockers via GPIO pins  
- Capture camera feeds using Pi Camera  
- Communicate with a Django backend for status updates and commands  
- Automatically update itself from GitHub  
- Run in **Docker containers** for easy deployment and reproducibility  

This system is **ready for bulk production** by cloning the SD card image to multiple devices.  

---

## Architecture

### Components

1. **Hardware Services**
   - `camera_service.py` → captures video, images, and sends data to backend
   - `locker_controller.py` → controls locker opening/closing via GPIO
2. **Docker**
   - Each service runs inside its own Docker container  
   - Uses volumes to store logs and data persistently  
3. **Update System**
   - `update.sh` → pulls the latest code from GitHub, installs dependencies, rebuilds containers
   - `start.sh` → runs services on boot
4. **CI/CD**
   - GitHub Actions pipeline builds multi-architecture Docker images (ARM for Pi)
   - Pushes images to Docker Hub
5. **Networking**
   - Services communicate with Django backend via HTTP API
   - Each device has a unique `DEVICE_ID` configured via `.env`

---

## Setup Instructions

### Prerequisites

- Raspberry Pi 4 (ARMv7/ARM64)  
- Raspberry Pi OS (64-bit recommended)  
- Docker & Docker Compose installed  

```bash
sudo apt update && sudo apt install -y docker.io docker-compose
sudo usermod -aG docker pi
sudo apt install git -y
