# Pilarm
Integrate existing door or window contact sensors with SmartThings using a Raspberry Pi or C.H.I.P.

# A note about the different "shards"

For the below steps be aware that different accounts use different URLs (shards). Please see <a href="https://community.smartthings.com/t/faq-how-to-find-out-what-shard-cloud-slice-ide-url-your-account-location-is-on/53923">FAQ: How to find out what “shard” (cloud slice IDE URL) your Account / Location is on?</a> for additional details and substitute the appropriate URL below.

## Setting up SmartThings Devices
1. Browse to https://graph.api.smartthings.com/ and login with your SmartThings account
2. On the top menu, click "My Device Handlers"
3. In the upper right, click "Settings"
4. Add a new Github repository with Owner = "rcoodey", name = "Pilarm" and Branch = "master"
5. In the upper right, click "Update from Repo" and choose "Pilarm"
6. Under the "New" section, check "devicetypes/rcoodey/pilarm-zone.src/pilarm-zone.groovy", check the "Publish" box and click "Execute Update"
7. On the top menu, click "My Devices"
8. In the upper right, click "+ New Device" and fill out the required items:
  * For "Device Network Id" enter "PilarmZone" followed by the GPIO number (ex. PilarmZone23)
  * For "Type" choose the newly added device type "Pilarm Zone"
9. Click "Create" and repeat for each door, window or other contact

## Setting up SmartThings SmartApp

1. Browse to https://graph.api.smartthings.com/ and login with your SmartThings account
2. On the top menu, click "My SmartApps"
3. In the upper right, click "Settings"
4. Add a new Github repository with Owner = "rcoodey", name = "Pilarm" and Branch = "master"
5. In the upper right, click "Update from Repo" and choose "Pilarm"
6. Under the "New" section, check "smartapps/rcoodey/pilarm.src/pilarm.groovy", check the "Publish" box and click "Execute Update"
7. Click the "Edit Properties" button to the left of the new SmartApp with name "rcoodey : Pilarm"
8. Click the "OAuth" section and click "Enable OAuth in Smart App"
9. Note down the "Client ID" and "Client Secret" and click "Update" at the bottom
10. Take the "Client ID" and plug into this URL "https://graph.api.smartthings.com/oauth/authorize?response_type=code&client_id=<INSERT YOUR ID>&redirect_uri=http://localhost&scope=app" and execute in a browser
11. Choose your hub in the dropdown and check all the contact sensors to participate in the alarm then click "Authorize"
12. The webpage will appear to not load (unless you are running a web server on your pc) but in the URL bar is the needed code: http://localhost/?code=P4FJGv
13. Take the above info and plug into this URL: "https://graph.api.smartthings.com/oauth/token?grant_type=authorization_code&client_id=<INSERT YOUR ID>&client_secret=<INSERT YOUR SECRET>&redirect_uri=http://localhost&code=<INSERT YOUR CODE>&scope=app" and execute in a browser
  * Copy the "access_token" from the JSON formatted  text and save for later use in the Pilarm Server config
14. The last item needed is the "SmartApp Id" which can be found from: https://graph.api.smartthings.com/api/smartapps/installations
  * In the JSON formatted text search for the "label" with name "Pilarm", just before this should be the "id"
  * Save this id for later use in the Pilarm Server config

## PilarmServer.py

If you're not on the main na shard, you might need to edit the URL in the PilarmServer.conf to reflect this, rather than using https://graph.api.smartthings.com/

## Getting started with Raspberry Pi
There is a lot of information out there about setting up a Raspberry Pi, so just a few high level details here.

1. Download and install Raspbian Lite (or I'm sure other distros will work if preferred)
  * https://www.raspberrypi.org/downloads/raspbian/
2. Change the default password: passwd
3. Setup WiFi if needed
  * https://thepihut.com/blogs/raspberry-pi-tutorials/83502916-how-to-setup-wifi-on-raspbian-jessie-lite
4. Optionally set a static IP, recommended if wanting to query contact states on demand
  * http://www.techsneeze.com/configuring-static-ip-raspberry-pi-running-raspbian/

## Attaching contacts to GPIO pins
1. Depending on the number of contacts to hookup, a bread broad is probably something to consider
2. Each contact should have two wires, attach one wire to GND
3. The other wire will attach to two things:
  * first to the desired GPIO pin
  * Second to a resistor (~10k for pull-up)
4. Connect the resistor to 3V3

<p align="center">
<img src="https://github.com/rcoodey/Pilarm/raw/master/images/AlarmBox.jpg" width="100" />
<img src="https://github.com/rcoodey/Pilarm/raw/master/images/BoardCenter.jpg" width="100" />
<img src="https://github.com/rcoodey/Pilarm/raw/master/images/BoardLeft.jpg" width="100" />
<img src="https://github.com/rcoodey/Pilarm/raw/master/images/BoardRight.jpg" width="100" />
</p>

## Setting up Python
1. Update apt-get: sudo apt-get update
2. Install Python 3: sudo apt-get -y install python3
3. Install library for working with GPIO pins: sudo apt-get -y install python3-rpi.gpio
4. Install library for sending HTTP requests: sudo apt-get -y install python3-requests

## Setting up Pilarm Server
1. Install Git: sudo apt-get -y install git-core
2. Download Pilarm Server files: git clone https://github.com/rcoodey/Pilarm.git
3. Make Python script executable: chmod 755 PilarmServer.py
4. Make shell script executable: chmod 755 PilarmServer.sh
5. Update settings in config file: nano PilarmServer.conf
  * Set "application_id" and "access_token" to those retrieved earlier during SmartApp setup
  * "Update_frequency" is used as a failsafe to refresh all contact sensor information. This time is in seconds and is recommend to not be set to low, the default is 30 seconds. Individual sensor (GPIO) changes should happen in near real-time and do not use this setting
  * For each GPIO used, enter the corresponding number in a comma separated list after "gpio_zones"
6. At this point it is recommended to test: sudo ./PilarmServer.py
  * Open and close some doors, you should see a message indicating the change
  * You should also see a message at each full update interval
7. Configure PilarmServer to start on boot: sudo nano /etc/rc.local
  * Add these two lines before "exit 0":
    /home/pi/PilarmServer.sh
    printf "Pil8arm started"
8. Reboot to start Pilarm always running in the background: sudo reboot

Let me know how this DIY alarm works and if you have any questions or issues.
