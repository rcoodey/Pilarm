/**
 *  Pilarm - Raspberry Pi Alarm for SmartThings
 *
 *  Copyright 2016 Ryan Coodey
 *
 *  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
 *  in compliance with the License. You may obtain a copy of the License at:
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
 *  on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License
 *  for the specific language governing permissions and limitations under the License.
 *
 */
 
definition(
    name: "Pilarm",
    namespace: "rcoodey",
    author: "Ryan Coodey",
    description: "Receives input changes from Raspberry Pi alarm server (Pilarm Server)",
    category: "Safety & Security",
    iconUrl: "https://s3.amazonaws.com/smartapp-icons/Convenience/Cat-Convenience.png",
    iconX2Url: "https://s3.amazonaws.com/smartapp-icons/Convenience/Cat-Convenience@2x.png",
    iconX3Url: "https://s3.amazonaws.com/smartapp-icons/Convenience/Cat-Convenience@2x.png",
    oauth: true)

preferences {
    section() { 
     	input "contactSensors", "capability.contactSensor", title: "Contact Sensors", multiple: true, required: false
	}
}

mappings { 
    path("/pilarm/zoneEvent/:state/:zone") { 
        action: [GET: "updateZone"] 
    } 
    path("/pilarm/allZonesEvent") { 
        action: [PUT: "updateAllZones"] 
    }
}

//Event handlers
void updateZone(state, zone) {
   def zonedevice = contactSensors.find { it.deviceNetworkId == "PilarmZone${zone}" } 
   if (zonedevice) {
       zonedevice.zoneEvent(state == "1" ? "open" : "closed")
       //log.debug "Zone ${zone} event: " + (event == "1" ? "open" : "closed")
   }
}

void updateZone() { 
   def state = params.state
   def zone = params.zone
   updateZone(state, zone)
   log.debug "Zone ${zone} state: " + (state == "1" ? "open" : "closed")
}

void updateAllZones() { 
   for(json in request.JSON) {
       def zone = json.getKey()
       def state = json.getValue()
       updateZone(state, zone)
   }
   log.debug "All zones event: " + request.JSON
}