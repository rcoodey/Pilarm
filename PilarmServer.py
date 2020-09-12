#!/usr/bin/env python3
import RPi.GPIO as GPIO 
import os
import configparser 
import time 
import requests 
import logging 
import socketserver 
import threading 
from http.server import BaseHTTPRequestHandler
import paho.mqtt.client as mqtt

#Open configuration file
config = configparser.ConfigParser()
script_dir = os.path.dirname(__file__) 
config.read(os.path.join(script_dir, 'PilarmServer.conf'))

#Get Pilarm settings and configure logging
gpio_zones = list(map(int, config.get('Pilarm', 'gpio_zones').split(',')))
log_file = config.get('Pilarm', 'log_file')
logging.basicConfig(filename=log_file, filemode='a', format="%(asctime)s %(levelname)s %(message)s", datefmt="%m-%d-%y %H:%M:%S", level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)
update_frequency = int(config.get('Pilarm', 'update_frequency'))
platform = config.get('Pilarm', 'platform') #smartthings, mqtt, both

def is_platform_smartthings():
    if platform == 'smartthings' or platform == 'both':
        return True
    return False

def is_platform_mqtt():
    if platform == 'mqtt' or platform == 'both':
        return True
    return False

#Get SmartThings settings
if is_platform_smartthings():
    smartthings_shard_url = config.get('SmartThings', 'shard_url')
    smartthings_application_id = config.get('SmartThings', 'application_id') 
    smartthings_access_token = config.get('SmartThings', 'access_token')
    smartthings_event_url = "https://" + smartthings_shard_url + "/api/smartapps/installations/" + smartthings_application_id + "/{0}/{1}?access_token=" + smartthings_access_token 
    smartthings_zone_event_url = smartthings_event_url.format("pilarm", "zoneEvent/{0}/{1}") 
    smartthings_all_zones_event_url = smartthings_event_url.format("pilarm", "allZonesEvent")

#Get MQTT setings
if is_platform_mqtt():
    mqtt_server = config.get('MQTT', 'server')
    mqtt_port = int(config.get('MQTT', 'port'))
    mqtt_username = config.get('MQTT', 'username')
    mqtt_password = config.get('MQTT', 'password')

#Handler for GPIO events
def gpio_handler(zone):
    try:
        if is_platform_smartthings():
            requests.get(smartthings_zone_event_url.format(GPIO.input(zone), zone))

        if is_platform_mqtt():
            mqttClient.publish('alarm/contact/' + str(zone), GPIO.input(zone))

        message = 'Zone ' + str(zone) + ' ' + ('opened' if GPIO.input(zone) else 'closed')
        print(message)
        logging.info(message)
    except Exception as e:
        logging.exception("Error processing GPIO event: " + str(e))

#Send MQTT update for all zones
def send_all_zones_mqtt():
    if is_platform_mqtt():
        for zone in gpio_zones:
            mqttClient.publish('alarm/contact/' + str(zone), GPIO.input(zone))

#Return JSON string for single zone (single option used if output will be combined with additional zones)
def get_zone_json(zone, single = True):
    json = '"' + str(zone) + '":"' + str(GPIO.input(zone)) + '"'
    if single:
        json = '{' + json + '}'
    return json

#Return JSON string for all zones
def get_all_zones_json():
    json = '{'
    for zone in gpio_zones:
        json = json + get_zone_json(zone, False)
        if zone == gpio_zones[-1]:
            json = json + '}'
        else:
            json = json + ','
    return json

#MQTT handlers
def on_connect(mosq, obj, rc):
    print("MQTT connection: " + str(rc))

def on_publish(client, userdata, result):
    print("Data published: " + str(result))

#Handler to parse and respond to incoming http requests
class GetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            #Get index for commands that need it
            index_split = self.path.split('/')
            index = None
            if len(index_split) > 2 and index_split[2].isdigit():
                index = int(index_split[2])
            
            #Parse URL for command and send response
            if '/GetZone' in self.path and index is not None:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(get_zone_json(index),'utf-8'))
            elif self.path == '/GetAllZones':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(get_all_zones_json(),'utf-8'))
           
        except Exception as e:
            logging.exception("Error processing HTTP request: " + str(e)) 

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
     pass 

#Begin Pilarm
logging.info('Initializing Pilarm')

#Setup using GPIO Broadcom SOC channel numbers
GPIO.setmode(GPIO.BCM)

#Do not need to see GPIO warnings
GPIO.setwarnings(False)

#Setup each GPIO pin that has a contact sensor and add event for instant push to SmartThings
for zone in gpio_zones:
    GPIO.setup(zone, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(zone, GPIO.BOTH, gpio_handler, bouncetime=200) 

#Setup and start http server
if is_platform_smartthings():
    httpServer = ThreadedTCPServer(("", 80), GetHandler) 
    http_server_thread = threading.Thread(target=httpServer.serve_forever)
    http_server_thread.daemon = True 
    http_server_thread.start()

#Setup MQTT client
if is_platform_mqtt():
    mqttClient = mqtt.Client("Pilarm")
    #mqttClient.on_connect = on_connect
    #mqttClient.on_publish = on_publish
    mqttClient.username_pw_set(mqtt_username, mqtt_password)
    mqttClient.connect(mqtt_server, mqtt_port)
    mqttClient.loop_start()

#Program loop to send status events to SmartThings
logging.info('Beginning Pilarm loop') 
while True:
    try:
        #Update all Pilarm zones on designated interval, this is an extra failsafe in the rare case a GPIO event is missed
        if is_platform_smartthings():
            requests.put(smartthings_all_zones_event_url, data=get_all_zones_json())
        if is_platform_mqtt():
            send_all_zones_mqtt()

        print("All zones event")

        #Wait for next loop
        time.sleep(update_frequency)
    
    #Handle all errors so alarm loop does not end
    except Exception as e:
        logging.exception("Error in alarm loop: " + str(e))
        print("Error in alarm loop: " + str(e))

#Stop Pilarm    
logging.info('Exited Pilarm loop and shutting down')

#Close down http server and GPIO registrations
httpServer.shutdown() 
httpServer.server_close() 
GPIO.cleanup()
