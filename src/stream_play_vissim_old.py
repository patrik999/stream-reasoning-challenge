#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt, sys
import optparse
import psycopg2
import shlex, subprocess
import time
from random import randint
import json

from osgeo import ogr
from shapely import *
from shapely.geometry import *
from shapely.wkt import *
#from shapely.wkb import *

connstr_pipedb = "host=localhost port=5433 dbname={0} user=patrik password=ps"


def main(argv):

    parser = optparse.OptionParser()
    #parser.add_option('--db', action="store", dest="namedb", default="ldm_2")
    parser.add_option('--sleep', action="store", dest="sleep", default=0.01) # 500ms
    parser.add_option('--start', action="store", dest="start", default=0)
    parser.add_option('--stop', action="store", dest="stop", default=500000)
    parser.add_option('--init', action="store", dest="init", default=0)
    parser.add_option('--tracefile', action="store", dest="tracefile", default="")
    parser.add_option('--modelfile', action="store", dest="modelfile", default="")
    parser.add_option('--out', action="store", dest="out", default=0)

    (options, args) = parser.parse_args()

    # Initialization
    trace_file = options.tracefile
    model_file = options.modelfile

    debug = False
    if(int(options.out) > 0):
    	debug = True

    #Read model file (encodeded in Datalog) and extract lanes with their geometries
    modelGeoDict = [] # {}

    model_file_cont = open(model_file)
    for model_line in model_file_cont:

    	line_raw = model_line.strip()
    	pos = line_raw.find("hasGeo") # hasGeo predicate
    	pos2 = line_raw.find(",\"") # first delimiter
    	pos3 = line_raw.find("\")") # second delimiter
    	if pos >= 0 and pos2 >= 0 and pos3 >= 0:

    		objID = line_raw[pos+7:pos2]
    		objGeoTxt =line_raw[pos2+2:pos3]

    		objGeo = loads(objGeoTxt)
    		if objGeo is not None:
    			#modelGeoDict[objID] = objGeo
    			modelGeoDict.append({'id': objID, 'geo': objGeo})

    		#print objID, objGeoTxt


    if not debug:
    	# Connection string
    	conn_1 =  connstr_pipedb.format(options.namedb)
    	# Connect to a PostGIS database and open a cursor to perform database operations
    	conn_pipedb = psycopg2.connect(conn_1)
    	# Set DB parameter
    	conn_pipedb.set_client_encoding('UTF8')
    	cur1 = conn_pipedb.cursor()


    # Value ranges
    val_stop = int(options.stop)
    val_start = int(options.start)
    val_sleep = float(options.sleep)
    start_ids = 300


    sqL_insert = "INSERT INTO {0} VALUES ({1},{2});"
    sqL_insert2 = "INSERT INTO {0} VALUES ({1},'{2}');"
    count = 0

    count_vehicles = 0

    # Open JSON file

    json_file = open(trace_file)
    json_str = json_file.read()
    json_data = json.loads(json_str)

    #for json_ in vehicles:
    json_traces = json_data['traces']

    print ("Start: ", len(json_traces))

    # traffic light changes every 4 steps
    tlChange = 4 # 4 # (2 / (val_sleep * 80))
    tlCount = tlChange

    # Iterate through each trace step
    for json_trace in json_traces:

    	count += 1
    	ind_id = 0

    	if count < val_start:
    		continue

    	start = time.time()

    	time.sleep(val_sleep)

    	rows_speed = []
    	rows_pos = []
    	rows_heading = []
    	#rows_spatial_rel = []

    	json_step = int(json_trace["step"])
    	json_vehicles = json_trace["vehicles"] #
    	json_signals= json_trace["signals"]

    	# Iterate through vehicles
    	for json_veh in json_vehicles:
    		ind_id = int(json_veh["VehicleID"])
    		veh_type = int(json_veh["VehicleType"])
    		mv_speed = json_veh["Speed"]
    		mv_long =  json_veh["Position_X"]
    		mv_lat =  json_veh["Position_Y"]
    		mv_heading = int(json_veh["Orient_Heading"])

    		if ind_id==0:
    			continue

    		veh_type_str = "car_"
    		ind_point = "" + str(mv_long) + " " +  str(mv_lat)
    		rows_speed.append({'iid': ind_id, 'x': mv_speed})
    		rows_pos.append({'iid': ind_id, 'x': ind_point})

    		mv_long = int(round(mv_long))
    		mv_lat = int(round(mv_lat))

    		veh_fullid = veh_type_str + str(ind_id)

    		if debug:
    			print ("speed(" + veh_fullid + "," + str(int(round(mv_speed))) + "," + str(json_step) +  ")")
    			print ("pos(" + veh_fullid + "," + str(mv_long) + "," + str(mv_lat) + "," + str(json_step) + ")")

    		# Calculate the lane where the car is currently located in (Output only to std:out, but can be extended to DB if needed)
    		vehicleGeoTxt = "POINT (" + str(mv_long) + " " + str(mv_lat) + ")"
    		vehicleGeo = loads(vehicleGeoTxt)

    		for tupleGeoDict in modelGeoDict:
    			objId = tupleGeoDict["id"]
    			objGeo = tupleGeoDict["geo"]
    			#objRel = ""

    			# Check within spatial relations, this can be extended with other relations such as crosses, intersects, touches, ...
    			if vehicleGeo.within(objGeo):
    				if debug:
    					print ("within(" + veh_fullid + "," + objId + "," + str(json_step) + ")")
    				#objRel = "within(" + objId + ")"

    			if vehicleGeo.crosses(objGeo):
    				if debug:
    					print ("crosses(" + veh_fullid + "," + objId + "," + str(json_step) + ")")
    				#objRel = "crosses(" + objId + ")"

    			if vehicleGeo.touches(objGeo):
    				if debug:
    					print ("touches(" + veh_fullid + "," + objId + "," + str(json_step) + ")")
    				#objRel = "touches(" + objId + ")"

    			#rows_spatial_rel.append({'iid': ind_id, 'x': objRel})

    		# Calculate heading (s,sw,w,...) of vehicles
    		mv_heading_dir = ""

    		if (mv_heading <= 3.141514 and mv_heading >= 3.12) or (mv_heading <= -3.12):
    			mv_heading_dir = "W"
    		if mv_heading <= 1.59 and mv_heading >= 1.55:
    		    mv_heading_dir = "N"
    		if mv_heading <= -1.55 and mv_heading >= -1.59:
    		    mv_heading_dir = "S"
    		if mv_heading <= 0.02 and mv_heading >= -0.02:
    		    mv_heading_dir = "E"
    		if mv_heading > 1.59 and mv_heading < 3.12:
    		    mv_heading_dir = "NW"
    		if mv_heading > -3.12 and mv_heading < -1.59:
    		    mv_heading_dir = "SW"
    		if mv_heading > 0.2 and mv_heading < 1.55:
    		    mv_heading_dir = "NE"
    		if mv_heading > -1.55 and mv_heading < -0.2:
    		    mv_heading_dir = "SE"

    		rows_heading.append({'iid': ind_id, 'x': mv_heading_dir}) # mv_heading_dirs
    		print ("heading(" + veh_fullid + "," + mv_heading_dir + "," + str(json_step) + ")")


    	if not debug:
    		cur1.executemany('INSERT INTO stream_speed (iid, x) VALUES (%(iid)s,%(x)s)', rows_speed)
    		cur1.executemany('INSERT INTO stream_pos (iid, x) VALUES (%(iid)s,%(x)s)', rows_pos)
    		cur1.executemany('INSERT INTO stream_heading (iid, x) VALUES (%(iid)s,%(x)s)', rows_heading)
    		#cur1.executemany('INSERT INTO stream_spatial_rel (iid, x) VALUES (%(iid)s,%(x)s)', rows_spatial_rel)


    	rows_sig = []


    	if tlCount >= tlChange:
    		tlCount = 0

    		# Iterate through traffic lights
    		for json_sig in json_signals:
    			sig_id1 = int(json_sig["ControllerId"])  # "_" +
    			sig_id2 = int(json_sig["SignalGroupID"]) # "_" +

    			if sig_id1 == 0:
    				continue

    			sig_id_nr = ""
    			sig_id = str(sig_id1) + str(sig_id2)
    			sig_state = int(json_sig["SignalState"])

    			# Convert CtrlID and SignalGroup to internal ids
    			if sig_id == "11":
    				sig_id_nr = "i100_sg1" # 36
    			elif sig_id == "12":
    				sig_id_nr = "i100_sg2" # 37
    			elif sig_id == "13":
    				sig_id_nr = "i100_sg3" # 38
    			elif sig_id == "14":
    				sig_id_nr = "i100_sg4" # 39
    			elif sig_id == "21":
    				sig_id_nr = "i200_sg1" # 86
    			elif sig_id == "22":
    				sig_id_nr = "i200_sg2" # 87
    			elif sig_id == "23":
    				sig_id_nr = "i200_sg3" # 88
    			elif sig_id == "24":
    				sig_id_nr = "i200_sg4" # 89
    			elif sig_id == "31":
    				sig_id_nr = "i300_sg1" # 136
    			elif sig_id == "32":
    				sig_id_nr = "i300_sg2" # 137
    			elif sig_id == "33":
    				sig_id_nr = "i300_sg3" # 138
    			elif sig_id == "34":
    				sig_id_nr = "i300_sg4" # 139
    			elif sig_id == "41":
    				sig_id_nr = "i400_sg1" # 186
    			elif sig_id == "42":
    				sig_id_nr = "i400_sg2" # 187
    			elif sig_id == "43":
    				sig_id_nr = "i400_sg3" # 188
    			elif sig_id == "44":
    				sig_id_nr = "i400_sg4" # 189

    			sig_state_txt = "0" # "Red"
    			# Red+Amber, Green, Amber, Off, Flashing Green
    			if sig_state == 2 or sig_state == 3 or sig_state == 4 or sig_state == 5 or sig_state == 9:
    				sig_state_txt = "1" # "Green"

    			if len(sig_id_nr) > 0:
    				rows_sig.append({'iid': sig_id_nr, 'x': sig_state_txt})
    				if debug:
    					print ("signalState(" + sig_id_nr + "," + sig_state_txt + ")")

    		if not debug:
    			cur1.executemany('INSERT INTO stream_signalState (iid, x) VALUES (%(iid)s,%(x)s)', rows_sig)

    	tlCount += 1


    end = time.time()


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
