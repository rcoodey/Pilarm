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

## Setting up SmartThings
1. Browse to https://graph.api.smartthings.com/ and login with your SmartThings account
2. On the top menu, click "My SmartApps"
3. In the upper right, click "Settings"
4. Add a new Github repositiry with Owner = "rcoodey", name = "Pilarm" and Branch = "master"
5. In the upper right, click "Update from Repo" and choose "Pilarm"
6. Under the "New" section, check "smartapps/rcoodey/pilarm.src/pilarm.groovy", check the "Publish" box and click "Execute Update"
7. Click the "Edit Properties" button to the left of the new SmartApp with name "rcoodey : Pilarm"
8. Click the "OAuth" section and click "Enable OAuth in Smart App"
9. Note down the "Client ID" and "Client Secret" and click "Update" at the bottom
10. Take the "Client ID" and plug into this URL "https://graph.api.smartthings.com/oauth/authorize?response_type=code&client_id=<INSERT YOUR ID>&redirect_uri=http://localhost&scope=app" and execute in a browser
11. Choose your hub in the dropdown and check all the contact sensors to participate in the alarm then click "Authorize"
12. The webpage will appear to not load (unless you are running a web server on your pc) but in the URL bar is the needed code: http://localhost/?code=P4FJGv
13. Take the above info and plug into this URL: "https://graph.api.smartthings.com/oauth/token?grant_type=authorization_code&client_id=<INSERT YOUR ID>&client_secret=<INSERT YOUR SECRET>&redirect_uri=http://localhost&code=<INSERT YOUR CODE>&scope=app" and execute in a browser
14. Copy the "Access Token" 

More steps coming soon...

## Setting up Pilarm Server
1. Install Git: sudo apt-get -y install git-core
2. Download Pilarm Server files: git clone https://github.com/rcoodey/Pilarm
3. Make Python script executable: chmod 755 PilarmServer.py
4. Make shell script executable: chmod 755 PilarmServer.sh

More steps coming soon...

## Setting up GPIO pins
Coming soon...
