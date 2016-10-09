#!/usr/bin/env python3
import RPi.GPIO as GPIO 
import configparser 
import time 
import requests 
import logging 
import socketserver 
import threading 
from http.server import BaseHTTPRequestHandler

#Open configuration file
config = configparser.ConfigParser() 
config.read('PilarmServer.conf')

#Get SmartThings settings
smartthings_application_id = config.get('SmartThings', 'application_id') 
smartthings_access_token = config.get('SmartThings', 'access_token') 
smartthings_update_frequency = int(config.get('SmartThings', 'update_frequency'))
smartthings_event_url = "https://graph.api.smartthings.com/api/smartapps/installations/" + smartthings_application_id + "/{0}/{1}?access_token=" + smartthings_access_token 
smartthings_zone_event_url = smartthings_event_url.format("pilarm", "zoneEvent/{0}/{1}") 
smartthings_all_zones_event_url = smartthings_event_url.format("pilarm", "allZonesEvent")

#Get Pilarm settings and configure logging
gpio_zones = map(int, config.get('Pilarm', 'gpio_zones').split(','))
log_file = config.get('Pilarm', 'log_file') 
logging.basicConfig(filename=log_file, filemode='a', format="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO) 
logging.getLogger("urllib3").setLevel(logging.WARNING)

#Handler for GPIO events
def gpio_handler(zone):
    try:
        requests.get(smartthings_zone_event_url.format(GPIO.input(zone), zone))
        print('Zone ' + str(zone) + ' ' + ('opened' if GPIO.input(zone) else 'closed'))
    except Exception as e:
        logging.exception("Error processing GPIO event: " + str(e))

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
httpServer = ThreadedTCPServer(("", 80), GetHandler) 
http_server_thread = threading.Thread(target=httpServer.serve_forever)
http_server_thread.daemon = True 
http_server_thread.start()

#Program loop to send status events to SmartThings
logging.info('Beginning Pilarm loop') 
while True:
    try:
        #Update all Pilarm zones on designated interval, this is an extra failsafe in the rare case a GPIO event is missed
        requests.put(smartthings_all_zones_event_url, data=get_all_zones_json())
        print("All zones event")
        
        #Wait for next loop
        time.sleep(smartthings_update_frequency)
    
    #Handle all errors so alarm loop does not end
    except Exception as e:
        logging.exception("Error in alarm loop: " + str(e))

#Stop Pilarm    
logging.info('Exited Pilarm loop and shutting down')

#Close down http server and GPIO registrations
httpServer.shutdown() 
httpServer.server_close() 
GPIO.cleanup()
