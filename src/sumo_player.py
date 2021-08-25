#!/usr/bin/env python


import os, sys, time
import optparse
import json
import uuid
import datetime

try:
    import thread
except ImportError:
    import _thread as thread

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

from abstract_player import AbstractPlayer # Import file


class SumoPlayer(AbstractPlayer):

    # Global variable
    step_ratio = 3
    steps_limit = 250
    sleep = 1.0
    config_name = ""
    templates = {}

    step = 0
    step2 = 0

    rows_pos = {}

    def __init__(self, sumo_config, template_dict):  # __init__
        self.streamID = sumo_config
        #self.templateID = template_path
        self.templates = template_dict


    def start(self, freq_in_ms):

        self.frequency = freq_in_ms

        # Inits
        count_vehicles = 0
        count = 0

        # traffic light only changes every 4 steps not every single time
        tlChange = 4
        tlCount = tlChange

        # Open template file
        print(str(self.templates))
        tempVehName = self.templates["subStreamVehicles"]
        #templ_file1 = open(tempVehName) #self.templateID
        templ_vehicles = open(tempVehName).read()

        # Template has to be split into platfrom/sensor parts using $CHILDS$
        tempTLName = self.templates["subStreamTrafficLights"]
        #templ_file2a = open(tempTLName)
        templ_TLs = open(tempTLName).read()

        tempTLName = self.templates["subStreamTrafficLightsChilds"]
        #templ_file2b = open(tempTLName)
        templ_TLs_Child = open(tempTLName).read()

        # Load tl positions from local dir
        file1 = open("./tl_mappings.config", "r")
        lines = file1.readlines()
        self.loadTLPositions(lines)

        # Open Sumo config file
        #config_file = open(self.streamID) # config_file
        #config_str = config_file.read()
        self.config_name = self.streamID

        #if options.nogui: #not
        sumoBinary = checkBinary('sumo')
        #else:
        #    sumoBinary = checkBinary('sumo-gui')

        print("Starting with ratio: " + str(self.step_ratio) + " and " + self.config_name)
        print("Limit steps: " + str(self.steps_limit))

        #global step, step2, plan_changes, plan_received

        # this is the normal way of using traci. sumo is started as a
        # subprocess and then the python script connects and runs
        sumoCmd = [sumoBinary, "-S", "-Q", "-c", self.config_name ]
        traci.start(sumoCmd)

        # TraCI control loop
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()

            self.step = self.step + 1
            time.sleep(self.sleep) # 0.5

            if(self.steps_limit < self.step):
                break

            if(self.step % self.step_ratio != 0):
                continue

            self.step2 = int(self.step / self.step_ratio)

            print("Step: " + str(self.step) + " / " + str(self.step2))

            vehicle_id_list = traci.vehicle.getIDList()
            print("Vehicles: " +  str(len(vehicle_id_list)))

            # Vehicles

            vehicles_ids=traci.vehicle.getIDList();

            for veh_id in vehicles_ids:
                #traci.vehicle.setSpeedMode(veh_id,0)
                #traci.vehicle.setSpeed(veh_id,15) #sets the speed of vehicles to 15 (m/s)

                replaceValues = {}
                replaceValues["$VehicleID$"] = str(veh_id)
                replaceValues["$ObsID$"] = "O_" + str(veh_id) + "-" + str(self.step)
                replaceValues["$Timestamp$"] = str(self.step)

                veh_speed = round(traci.vehicle.getSpeed(veh_id), 3)
                replaceValues["$Speed$"] = str(veh_speed)
                veh_type = traci.vehicle.getTypeID(veh_id)
                replaceValues["$Type$"] = str(veh_type)
                veh_acc = round(traci.vehicle.getAcceleration(veh_id), 4)
                replaceValues["$Accel$"] = str(veh_acc)
                veh_angle = round(traci.vehicle.getAngle(veh_id), 4)
                replaceValues["$Orient_Heading$"] = str(veh_angle)
                veh_pos = traci.vehicle.getPosition(veh_id)
                #veh_pos = veh_pos.replace('(','').replace('','').strip()

                #posXY = veh_pos.split(',')
                replaceValues["$Position_X$"] = str(round(veh_pos[0],5))
                replaceValues["$Position_Y$"] = str(round(veh_pos[1],5))

                veh_signals = traci.vehicle.getSignals(veh_id)
                veh_lane = str(traci.vehicle.getLaneID(veh_id)) + ";" + str(round(traci.vehicle.getLanePosition(veh_id), 4))

                #print("Speed ", veh_id, ": ", veh_speed, " m/s")
                #print("EdgeID of veh ", veh_id, ": ", traci.vehicle.getRoadID(veh_id))
                #print('Distance ', veh_id, ": ", traci.vehicle.getDistance(veh_id), " m")

                # Speed
                #print(templ_vehicles)
                msg1 = templ_vehicles
                for key, val in replaceValues.items():
                    msg1 = msg1.replace(key,val)
                print(msg1)
                yield msg1

                #msg1a = "speed(" + str(self.step2) + "," + str(veh_id) + "," + str(veh_speed) + ") ."
                #yield msg1a

            # Lanes
            lane_id_list = traci.lane.getIDList()

            # Traffic lights
            tl_id_list = traci.trafficlight.getIDList()

            # Group of traffic lights
            for intersID in tl_id_list:

                msg2 = templ_TLs.replace("$IntersectionID$",str(intersID))
                msg2_Childs = ""

                replaceValues2 = {}
                #replaceValues2["$IntersectionID$"] = str(intersID)
                replaceValues2["$Timestamp$"] = str(self.step)

                # Get signals for one intersection
                tl_states = traci.trafficlight.getRedYellowGreenState(intersID)
                #msg2 = "tlPhase(" + str(self.step2) + "," + str(tl_id) + "," + tl_states + ")"

                if(intersID in self.rows_pos):
                    row_pos = self.rows_pos[intersID]

                    # Find tlight for position
                    for row_pos in self.rows_pos: # row_pos is at tuple (tlid positions)
                        tl_id = row_pos[0]
                        tl_pos_dict = row_pos[1]

                        for i in range(0, len(tl_states)): # each char is one signal state

                            tlState = tl_states[i]
                            if i in tl_pos_dict:
                                replaceValues2["$TrafficLightID$"] = str(tl_id)
                                replaceValues2["$SignalState$"] = str(tlState)

                                msg2_Temp = templ_TLs_Child

                                for key, val in replaceValues2.items():
                                    msg2_Temp = msg2_Temp.replace(key,val)

                                if(len(msg2_Childs) > 0):
                                    msg2_Childs = msg2_Childs + ", \n"
                                msg2_Childs = msg2_Childs + msg2_Temp

                if(len(msg2_Childs) > 0):
                    msg2 = msg2.replace("$CHILDS$", str(msg2_Childs))
                    yield msg2

            #for lane_id in lane_id_list:
                #lane_count = int(traci.lane.getLastStepVehicleNumber(lane_id))

                #if(lane_count > 0):

                    # Merge lanes to road
                    #msg2 = "info(VehicleCount," + str(self.step2) + "," + str(lane_id) + "," + str(lane_count) + ")"
                    #yield msg2
                    #if(not ws is None):
                        #ws.send(msg1)

                    #waiting_count = int(traci.lane.getWaitingTime(lane_id))

                    #if(waiting_count > 0):
                        #msg3 = "info(WaitingTime," + str(self.step2) + "," + str(lane_id) + "," + str(waiting_count) + ")"
                        #yield msg3
                        #if(not ws is None):
                        #    ws.send(msg2)



        traci.close()
        sys.stdout.flush()


    def modify(self, freq_in_ms):
        self.frequency = freq_in_ms


    def loadTLPositions(self, linesBasePlan): #  namePlan, nameChg factor,

        for line1 in  linesBasePlan: # f_open1:

            line1=line1.strip()

            if len(line1) == 0:
                continue

            if line1.find("pos") >= 0:

                posHead2 = len("pos") + 1
                posEnd2 = len(line1) - 2
                lineData2 = line1[posHead2:posEnd2]

                lineDataSplit = lineData2.split(',')
                intersID = lineDataSplit[0].strip()
                laneID = lineDataSplit[1].strip()
                posString = lineDataSplit[2].strip()
                posDict = {}
                for x in posString.split(";"):
                    posDict[x] = ""

                row = {'lane': laneID,  'pos': posDict } # 'inters': insID,

                if intersID in self.rows_pos:
                    self.rows_pos[intersID].append(row)
                else:
                    rows = []
                    rows.append(row)
                    self.rows_pos[intersID] = rows


def main(argv):


    parser = optparse.OptionParser()
    parser.add_option('--nogui', action="store_true", dest="nogui", default=False, help="Run the commandline version of sumo")

    templates = {}
    templates["subStreamVehicles"] = "../stream-templates/traffic/vehicle_template.json"
    templates["subStreamTrafficLights"] = "../stream-templates/traffic/traffic_light_template.json"
    templates["subStreamTrafficLightsChilds"] = "../stream-templates/traffic/traffic_light_template2.json"

    player = SumoPlayer("../stream-log-files/sumo/testASP_30.sumocfg", templates)

    print("Start streaming...")

    for msg in player.start(0.5): # 0.1
        print(msg)

    print("Stop streaming.")

    player.close()

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
