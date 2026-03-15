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

### Install

Download the script

```bash
wget https://raw.githubusercontent.com/rueedlinger/amwa/refs/heads/main/scripts/install.sh -O install.sh
```

Make it executable

```bash
chmod +x install.sh
```

Run it

```bash
sudo ./install.sh
```

The script will 
- git clone the repo
- build python and node
- configure usb
  - add User to `plugdev` Group
  - create a udev rule for the ANT+ usb adapter
- create systemctl service


sudo vim /etc/systemd/system/wifi-powersave@.service

[Unit]
Description=Set WiFi power save %i
After=sys-subsystem-net-devices-wlan0.device

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/iw dev wlan0 set power_save %i

[Install]
WantedBy=sys-subsystem-net-devices-wlan0.device

sudo systemctl daemon-reload

sudo systemctl start wifi-powersave@on.service
sudo systemctl stop wifi-powersave@off.service

sudo systemctl enable wifi-powersave@off.service

systemctl status wifi-powersave@off.service