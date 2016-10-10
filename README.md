# Pilarm
Integrate existing door or window contact sensors with SmartThings using a Raspberry Pi or C.H.I.P.

## Getting started with Raspberry Pi
There is a lot of information out there about setting up a Raspberry Pi, so just a few high level details here.

1. Download and install Raspbian Lite (or I'm sure other distros will work if preferred)
  * https://www.raspberrypi.org/downloads/raspbian/
2. Change the default password: passwd
3. Setup WiFi if needed
  * https://thepihut.com/blogs/raspberry-pi-tutorials/83502916-how-to-setup-wifi-on-raspbian-jessie-lite
4. Optionally set a static IP, recommended if wanting to query contact states on demand
  * http://www.techsneeze.com/configuring-static-ip-raspberry-pi-running-raspbian/
  
## Setting up Python
1. Update apt-get: sudo apt-get update
2. Install Python 3: sudo apt-get -y install python3
3. Install library for working with GPIO pins: sudo apt-get -y install python3-rpi.gpio
4. Install library for sending HTTP requests: sudo apt-get -y install python3-requests

## Setting up Pilarm Server
Coming soon...
