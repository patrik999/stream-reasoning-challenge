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

    step = 0
    step2 = 0

    def init(self, stream_path, template_path):  # __init__
        self.streamID = stream_path
        self.templateID = template_path


    def start(self, freq_in_ms):

        self.frequency = freq_in_ms

        # Inits
        count_vehicles = 0
        count = 0

        # traffic light only changes every 4 steps not every single time
        tlChange = 4
        tlCount = tlChange

        # Open template file
        templ_file = open(self.templateID)
        templ_str = templ_file.read()

        # Open Sumo config file
        #config_file = open(self.streamID) # config_file
        #config_str = config_file.read()
        self.config_name = self.streamID

        #self.step_ratio = int(options.stepratio)
        #self.steps_limit = int(options.limit)
        #self.sleep = float(options.sleep)

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

                veh_speed = round(traci.vehicle.getSpeed(veh_id), 3)
                veh_acc = round(traci.vehicle.getAcceleration(veh_id), 4)
                veh_pos = traci.vehicle.getPosition(veh_id)
                veh_type = traci.vehicle.getTypeID(veh_id)
                veh_signals = traci.vehicle.getSignals(veh_id)
                veh_lane = str(traci.vehicle.getLaneID(veh_id)) + ";" + str(traci.vehicle.getLanePosition(veh_id))
                #print("Speed ", veh_id, ": ", veh_speed, " m/s")
                #print("EdgeID of veh ", veh_id, ": ", traci.vehicle.getRoadID(veh_id))
                #print('Distance ', veh_id, ": ", traci.vehicle.getDistance(veh_id), " m")

                # Speed
                msg1a = "info(VehSpeed," + str(self.step2) + "," + str(veh_id) + "," + str(veh_speed) + ")"
                yield msg1a

                msg1b = "info(VehAcc," + str(self.step2) + "," + str(veh_id) + "," + str(veh_acc) + ")"
                yield msg1b

                msg1c = "info(VehPos," + str(self.step2) + "," + str(veh_id) + "," + str(veh_pos) + ")"
                yield msg1c

                msg1d = "info(VehType," + str(self.step2) + "," + str(veh_id) + "," + str(veh_type) + ")"
                yield msg1d

                msg1e = "info(VehSignals," + str(self.step2) + "," + str(veh_id) + "," + str(veh_signals) + ")"
                yield msg1e

                msg1d = "info(VehLane," + str(self.step2) + "," + str(veh_id) + "," + veh_lane + ")"
                yield msg1d

                #if(not ws is None):
                    #ws.send(msg1)


            # Lanes
            lane_id_list = traci.lane.getIDList()

            for lane_id in lane_id_list:
                lane_count = int(traci.lane.getLastStepVehicleNumber(lane_id))

                if(lane_count > 0):

                    # Merge lanes to road
                    #msg2 = "info(VehicleCount," + str(self.step2) + "," + str(lane_id) + "," + str(lane_count) + ")"
                    #yield msg2
                    #if(not ws is None):
                        #ws.send(msg1)

                    waiting_count = int(traci.lane.getWaitingTime(lane_id))

                    if(waiting_count > 0):
                        msg3 = "info(WaitingTime," + str(self.step2) + "," + str(lane_id) + "," + str(waiting_count) + ")"
                        yield msg3
                        #if(not ws is None):
                        #    ws.send(msg2)

            # Traffic lights
            tl_id_list = traci.trafficlight.getIDList()

            for tl_id in tl_id_list:

                tl_state = traci.trafficlight.getRedYellowGreenState(tl_id)
                msg1 = "info(TLPhase," + str(self.step2) + "," + str(tl_id) + "," + tl_state + ")"

                #
                #if(ws not is None):
                #    ws.send(msg1)
                yield msg1


        traci.close()
        sys.stdout.flush()


    def modify(self, freq_in_ms):
        self.frequency = freq_in_ms


def main(argv):


    parser = optparse.OptionParser()
    parser.add_option('--nogui', action="store_true", dest="nogui", default=False, help="Run the commandline version of sumo")

    player = SumoPlayer("../stream-log-files/sumo/testASP_30.sumocfg", "../stream-templates/traffic/sumo_vehicle_template.json")

    print("Start streaming...")

    for msg in player.start(0.5): # 0.1
        print(msg)

    print("Stop streaming.")

    player.close()

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
