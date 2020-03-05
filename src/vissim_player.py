#!/usr/bin/env python

import getopt, sys
import optparse
import time
import abstract_player # Import file
import json

class VissimPlayer(AbstractPlayer):



    def init(self, stream_path, template_path):  # __init__
        self.streamID = stream_path
        self.templateID = template_path


    def start(self, freq_in_ms):

        self.frequency = freq_in_ms

        # Inits
        count_vehicles = 0
        # traffic light only changes every 4 steps not every single time
        tlChange = 4 # 4 # (2 / (val_sleep * 80))
        tlCount = tlChange

        # Open template file
        templ_file = open(self.templateID)
        templ_str = templ_file.read()

        # Open JSON file
        json_file = open(self.streamID)
        json_str = json_file.read()
        json_data = json.loads(json_str)

        #for json_ in vehicles:
        json_traces = json_data['traces']

        print ("Start Vissim trace: ", len(json_traces))

        # Iterate through each trace step
        for json_trace in json_traces:

        	count += 1
        	ind_id = 0

        	#if count < val_start:
        	#	continue

        	start = time.time()

        	time.sleep(self.frequency)

        	rows_speed = []
        	rows_pos = []
        	rows_heading = []

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

        		#rows_speed.append({'iid': ind_id, 'x': mv_speed})
        		#rows_pos.append({'iid': ind_id, 'x': ind_point})

        		mv_long = int(round(mv_long))
        		mv_lat = int(round(mv_lat))

        		veh_fullid = veh_type_str + str(ind_id)

        		# Calculate the lane where the car is currently located in (Output only to std:out, but can be extended to DB if needed)
        		vehicleGeoTxt = "POINT (" + str(mv_long) + " " + str(mv_lat) + ")"
        		#vehicleGeo = loads(vehicleGeoTxt)

        		#rows_heading.append({'iid': ind_id, 'x': mv_heading_dir})

                yield msgVehicle


            # Init signals
        	rows_sig = []

            #
        	if tlCount >= tlChange:
        		tlCount = 0

        		# Iterate through traffic lights
        		for json_sig in json_signals:
        			sig_id1 = int(json_sig["ControllerId"])  # "_" +
        			sig_id2 = int(json_sig["SignalGroupID"]) # "_" +

                    # Ignore signal0
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
        				#rows_sig.append({'iid': sig_id_nr, 'x': sig_state_txt})
                        yield msgVehicle



        	tlCount += 1


    def modify(self, freq_in_ms):
        self.frequency = freq_in_ms


def main(argv):

    player = VissimPlayer("SID", "TID")

    print("Start streaming...")

    for msg in player.start(0): # 0.1
        print(msg)

    print("Stop streaming.")

    player.close()

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
