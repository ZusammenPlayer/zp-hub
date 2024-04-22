# zp-hub

## Usage

### create image

The easiest way to setup a client is to use the provided image for a raspberry pi 4. In this section we describe how to setup your own client.

**Prerequisites**

- Raspberry Pi 4
- SD-Card
- Internet connection
- RaspberryPi Imager [https://github.com/raspberrypi/rpi-imager](https://github.com/raspberrypi/rpi-imager)

**prepare sd card and install operating system**

- use RaspberryPi Imager to install the latest version of RaspberryPi OS
  - in Settings, you can specify various configuration parameter such as keys for ssh access or WiFi. Leave the host name empty, since it will be defined at boot time of the pi and will include the mac adress of your device
- put the SD-Card into your RaspberryPi and boot it up
- it's a good practice to update all software packages, so login to your raspberrypi either via SSH or via keyboard if it is already connected to a monitor
- open a terminal and execute: `$sudo apt udpate` and then `$sudo apt upgrade`

### deploy backend and frontend packages

We have defined several directories where we store project relevant files and packages, which we will use throughout this documentation.

- create a folder `zp-hub` in `/opt`
  - `$sudo mkdir /opt/zp-hub`
  - change folder permissions: `sudo chown pi:pi /opt/zp-hub`
- deploy backend scripts
  - create folder `backend`: `$mkdir /opt/zp-hub/backend`
  - create folder `releases`: `$mkdir /opt/zp-hub/backend/releases`
  - copy the latest release of zp-hub backend to releases folder
    - use the deploy script in the backend folder and use your ssh config name for the PI as command line argument
    - `./deploy_to_hub.sh <config-name>`
  - make adaptations in your config.py in the src folder (you might need to create this file)
  - start the backend with: `python3 /opt/zp-hub/backend/releases/src/app.py`
- deploy frontend scripts
  - important! Use Nodejs v20.11.1 (LTS) or higher to run the following scripts!
  - create folder `frontend`: `$mkdir /opt/zp-hub/frontend`
  - create folder `releases`: `$mkdir /opt/zp-hub/frontend/releases`
  - use the deploy script in the frontend folder also followed by the name of the ssh config for the PI (same as for the backend)
  - `./deploy_to_hub.sh <config-name>`

- point your browser to the ip of the PI where you just deployed your scripts: `http://<ip-of-hub>:8080`
