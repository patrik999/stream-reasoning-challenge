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
        
    
class AbstractAdapter(object):
    
    def __init__(self, path_to_log, path_to_event_template, path_to_vehicle_template):
        self.event_template = open(path_to_event_template, 'r').read()
        self.vehicle_template = open(path_to_vehicle_template, 'r').read()
        self.event_log = open(path_to_log, 'r').read()
        
    #read log file and generate an array of events
    def __read_log_file__(self):
        pass
    
    #convert an event into given format
    def __convert_event__(self, event, eventId):
        pass
            
    def read_event(self):
        events = self.__read_log_file__()
        for event in events:
            eventId = uuid.uuid1()
            yield self.__convert_event__(event, eventId)    
    
    
#convert into RDF data
class RDFAdapter(AbstractAdapter):
    
    def __init__(self, path_to_log, path_to_event_template, path_to_vehicle_template):
        super(RDFAdapter, self).__init__(path_to_log, path_to_event_template, path_to_vehicle_template)
    
    #describe a vehicle in RDF
    def __convert_vehicle_rdf__(self, vehicle, obsID, timestep):
        s = self.vehicle_template
        s = s.replace("$VehicleID$",      str(vehicle['id']))
        s = s.replace("$obsMoveID$",      str(obsID) + "_" + str(vehicle['id']))
        s = s.replace("$obsGPSID$",       str(obsID) + "_" + str(vehicle['id']))
        s = s.replace("$resultId$",       str(obsID) + "_" + str(vehicle['id']))
        s = s.replace("$dateTime$",       str(timestep))
        s = s.replace("$Speed$",          str(vehicle['speed']))
        s = s.replace("$Position_X$",     str(vehicle['x']))
        s = s.replace("$Position_Y$",     str(vehicle['y']))
        s = s.replace("$Orient_Heading$", str(vehicle['angle'])) 
        return s     
      
    def __convert_event__(self, event, eventId):
        vehicles = event['vehicles']
        timestep = event['timestep']
        event_rdf = self.event_template
        
        vehicles_rdf = self.__convert_vehicles__(vehicles, eventId, timestep)
        event_rdf = event_rdf.replace("\"$Vehicles$\"", vehicles_rdf)
        return event_rdf    
    
    
    
class SumoAdapter(RDFAdapter):
    
    def __init__(self, path_to_log, path_to_event_template, path_to_vehicle_template):
        super(SumoAdapter, self).__init__(path_to_log, path_to_event_template, path_to_vehicle_template)
    
    #read sumo log file
    def __read_log_file__(self):
        events = []
        root = ET.fromstring(self.event_log)
        for event_sumo in root.findall('timestep'):
            event             = {}
            event['timestep'] = str(datetime.now(pytz.utc).isoformat());
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
    
    
    
    
    
class SumoRDFAdapter(SumoAdapter):
    
    def __init__(self, path_to_log, path_to_event_template, path_to_vehicle_template):
        super(SumoRDFAdapter, self).__init__(path_to_log, path_to_event_template, path_to_vehicle_template)
    
    #describe a vehicle in RDF
    def __convert_vehicle_rdf__(self, vehicle, obsID, timestep):
        s = self.vehicle_template
        s = s.replace("$VehicleID$",      str(vehicle['id']))
        s = s.replace("$obsMoveID$",      str(obsID) + "_" + str(vehicle['id']))
        s = s.replace("$obsGPSID$",       str(obsID) + "_" + str(vehicle['id']))
        s = s.replace("$resultId$",       str(obsID) + "_" + str(vehicle['id']))
        s = s.replace("$dateTime$",       str(timestep))
        s = s.replace("$Speed$",          str(vehicle['speed']))
        s = s.replace("$Position_X$",     str(vehicle['x']))
        s = s.replace("$Position_Y$",     str(vehicle['y']))
        s = s.replace("$Orient_Heading$", str(vehicle['angle'])) 
        return s     
      
    def __convert_event__(self, event, eventId):
        vehicles = event['vehicles']
        timestep = event['timestep']
        event_rdf = self.event_template
        
        vehicles_rdf = self.__convert_vehicles__(vehicles, eventId, timestep)
        event_rdf = event_rdf.replace("\"$Vehicles$\"", vehicles_rdf)
        return event_rdf    
    
    
    
class SumoJsonLdAdapter(SumoRDFAdapter):
       
    def __init__(self, path_to_log):
        super(SumoJsonLdAdapter, self).__init__(path_to_log,
                                                "../stream-templates/traffic/sumo_event_template.json", 
                                                "../stream-templates/traffic/sumo_vehicle_template.json")
    #describe all vehicles in JsonLD format
    def __convert_vehicles__(self, vehicles, obsID, timestep):
        s = ""
        for vehicle in vehicles:
            s = s + self.__convert_vehicle_rdf__(vehicle, obsID, timestep) + ",\n"
            s = s[:-2]    
        return s
    
    
    
class SumoNTriplesAdapter(SumoRDFAdapter):
       
    def __init__(self, path_to_log):
        super(SumoNTriplesAdapter, self).__init__(path_to_log,
                                                "../stream-templates/traffic/event_template.nt", 
                                                "../stream-templates/traffic/vehicle_template.nt")
        
    def __convert_vehicles__(self, vehicles, obsID, timestep):
        s = ""
        for vehicle in vehicles:
            s = s + self.__convert_vehicle_rdf__(vehicle, obsID, timestep) 
        return s 
    