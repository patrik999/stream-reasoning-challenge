import json
import xml.etree.ElementTree as ET


def read_sumo_log_file(path_to_sumo_log):
    events = []
    with open(path_to_sumo_log, 'r') as sumo_log:
        tree = ET.parse(sumo_log)
        root = tree.getroot()
        for event_sumo in root.findall('timestep'):
            event             = {}
            event['timestep'] = event_sumo.attrib['time']
            vehicles          = []
            for vehicle_sumo in event_sumo:
                vehicle          = {}
                vehicle['id']    = vehicle_sumo.attrib['id']
                vehicle['x']     = vehicle_sumo.attrib['x']
                vehicle['y']     = vehicle_sumo.attrib['y']
                vehicle['angle'] = vehicle_sumo.attrib['angle']
                vehicle['speed'] = vehicle_sumo.attrib['speed']
                vehicles.append(vehicle)
            event['vehicles'] = vehicles
            events.append(event)
    return events;



def convert_vehicle_rdf(vehicle, template, observationID, timestep):
    s = template
    s = s.replace("$VehicleID$", str(vehicle['id']))
    s = s.replace("$obsMoveID$", str(observationID) + "_" + str(vehicle['id']))
    s = s.replace("$obsGPSID$", str(observationID) + "_" + str(vehicle['id']))
    s = s.replace("$resultId$", str(observationID) + "_" + str(vehicle['id']))
    s = s.replace("$dateTime$",  str(timestep))
    s = s.replace("$Speed$", str(vehicle['speed']))
    s = s.replace("$Position_X$", str(vehicle['x']))
    s = s.replace("$Position_Y$", str(vehicle['y']))
    s = s.replace("$Orient_Heading$", str(vehicle['angle'])) 
    return s  

                  
    
def convert_vehicle_jsonld(vehicle, observationID, timestep):
    vehicle_json_template_path = "../stream-templates/traffic/sumo_vehicle_template.json"
    template      = open(vehicle_json_template_path, 'r').read()
    return convert_vehicle_rdf(vehicle, template, observationID, timestep)



def convert_vehicles_jsonld(vehicles, observationID, timestep):
    s = ""
    for vehicle in vehicles:
        s = s + convert_vehicle_jsonld(vehicle, observationID, timestep) + ",\n"
    s = s[:-2]    
    return s

def convert_event_jsonld(event, eventID):
    event_jsonld_template_path = "../stream-templates/traffic/sumo_event_template.json"
    event_jsonld = open(event_jsonld_template_path, 'r').read()
    timestep = event['timestep']
    vehicles = event['vehicles']
    vehicles_jsonld = convert_vehicles_jsonld(vehicles, eventID, timestep)
    event_jsonld = event_jsonld.replace("\"$Vehicles$\"", vehicles_jsonld)
    return event_jsonld    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    