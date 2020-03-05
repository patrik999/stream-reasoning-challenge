import json
import pytz
from datetime import datetime

trace_jsonld_template_path   = "stream-reasoning-challenge/stream-templates/traffic/trace_template.json"
trace_jsonld_template        = open(trace_jsonld_template_path, 'r').read()

vehicle_jsonld_template_path = "stream-reasoning-challenge/stream-templates/traffic/vehicle_template.json"
vehicle_jsonld_template      = open(vehicle_jsonld_template_path, 'r').read()


def fromTrace(trace):
    trace_jsonld = trace_jsonld_template
    
    vehicles_jsonld = fromVehicles(trace['vehicles'], trace['step'])
    #signals_jsonld  = fromSignals(trace['signals'])
    
    trace_jsonld = trace_jsonld.replace("\"$Vehicles$\"", vehicles_jsonld)
    #trace_jsonld = trace_jsonld.replace("\"$Signals$\"", signals_jsonld)
    
    trace_jsonld = trace_jsonld.replace("$step$", str(trace['step']))
    
    
    return trace_jsonld


def fromVehicles(vehicles, step):
    vehicles_jsonld = ""
    
    for vehicle in vehicles:
        vehicles_jsonld = vehicles_jsonld + fromVehicle(vehicle, step) + ",\n"
    
    vehicles_jsonld = vehicles_jsonld[:-2]
    return vehicles_jsonld
    

def fromVehicle(vehicle, step):
    xmldatetime = str(datetime.now(pytz.utc).isoformat());
    
    s = vehicle_jsonld_template;
    s = s.replace("$VehicleID$", str(vehicle['VehicleID']))
    s = s.replace("$obsMoveID$", str(step) + "_" + str(vehicle['VehicleID']))
    s = s.replace("$obsGPSID$" , str(step) + "_" + str(vehicle['VehicleID']))
    s = s.replace("$resultId$" , str(step) + "_" + str(vehicle['VehicleID']))
    s = s.replace("$dateTime"  , xmldatetime)
    s = s.replace("$Speed$", str(vehicle['Speed']))
    s = s.replace("$Position_X$", str(vehicle['Position_X']))
    s = s.replace("$Position_Y$", str(vehicle['Position_Y']))
    s = s.replace("$Orient_Heading$", str(vehicle['Orient_Heading']))
    return s;        

filePath = 'stream-reasoning-challenge/stream-log-files/traffic/trace_T1_light.json'

i=0;
with open(filePath) as json_file:
    data = json.load(json_file)
    for trace in data['traces']:
        trace_s = fromTrace(trace)
        #TODO : wsSocker.send(trace_s)
        i += 1;
        if (i==10):
            break;
        print(trace_s)
       