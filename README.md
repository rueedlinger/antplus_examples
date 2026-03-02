# ANT+ Metrics Web Application (amwa)

This project is a **FastAPI** and **Vue.js** web application designed to run on Raspberry Pi OS Lite.

It provides real-time visualization and monitoring of ANT+ sensor data through a lightweight web interface.

## Features

- Display of ANT+ sensor data:
  - Power
  - Speed
  - Cadence
  - Heart Rate
  - Distance
- Built-in time display
- Configurable interval timer
- Web-based dashboard (accessible via browser)

## Technology Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Vue.js (Node)
- **ANT+ Communication:** https://github.com/Tigge/openant
- **Platform:** Raspberry Pi OS Lite (Debian-based, no desktop environment)



## Requirements
- ANT+ USB adapter (eg. Tacx ANT+ Antenne, etc.)
- Pythopn
- Node


## Setup
### Raspberry Pi OS Lite

I am using **Raspberry Pi OS Lite**.

- A minimal, lightweight operating system  
- Based on a port of **Debian Trixie**  
- No desktop environment (command-line only)

Update instructions and official documentation:  
- https://www.raspberrypi.com/documentation/

### User

If the default `pi` user does not exist or you want to create a new user with the same name:

```bash
sudo adduser pi
```

Give the new user administrative privileges:

```bash
sudo usermod -aG sudo pi
```

### Update Your System
Before installing anything, update and upgrade your system packages:

```bash
sudo apt update
sudo apt full-upgrade -y
```

Install Python, Node.js, npm, and Git:

```bash
sudo apt install nodejs npm git python3 python3-pip vim -y
```

### Configure USB 

To allow non-root access to the ANT+ USB adapter on Raspberry Pi OS Lite, follow these steps:

Add User to `plugdev` Group:

```bash
sudo usermod -aG plugdev pi
```

Log out and back in for the group changes to take effect.

Plug in the ANT+ USB adapter and check that it is detected:

```bash
lsusb
```
Expected output (example):
```bash
Bus 001 Device 004: ID 0fcf:1008 Dynastream Innovations, Inc. ANTUSB2 Stick
```

Create udev Rule
```bash
sudo vim /etc/udev/rules.d/99-antusb.rules
```
Add the following line, but adapt to your `idVendor` and `idProduct` based on the `lsusb` output.

```
SUBSYSTEM=="usb", ATTR{idVendor}=="0fcf", ATTR{idProduct}=="1008", GROUP="plugdev", MODE="0660"
```

Apply the new rule:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Unplug and replug the ANTUSB2 Stick. Check that the device now belongs to the plugdev group:

```bash
ls -l /dev/bus/usb/001/004
````

Example output:

```bash
crw-rw---- 1 root plugdev 189, 4  1. Mär 21:46 /dev/bus/usb/001/004
```

### Create a Systemd Service for Auto-Start

You can run your ANT+ metrics app on boot using a **systemd service**.

Open a new systemd service:

```bash
sudo vim /etc/systemd/system/mystart.service
```

Add the following content:

```
[Unit]
Description=My Startup Script
After=network.target

[Service]
ExecStart=/home/pi/amwa/start.sh
WorkingDirectory=/home/mr/amwa
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```


## Test
### Test Install Script with Docker
```bash
docker build --build-arg CACHE_BUST=$(date +%s) -t app:latest .
docker run -it --rm -p 8000:8000 app:latest bash
```

Then test the install script
```bash
./install.sh 
```

Or directly with

```bash
docker build --build-arg CACHE_BUST=$(date +%s) -t app:latest .
docker run -it --rm -p 8000:8000 app:latest /app/install
```


