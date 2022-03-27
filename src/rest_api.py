import threading
from custom_websocket_server import WSServer
from flask import Flask, json, request, abort
from runpy import run_path
from distutils.util import strtobool
import os
ROOT_PATH = os.path.abspath(os.curdir) + "/"


class RestApi():
    config = None

    def __init__(self, config):
        self.config = config
        # init rest api
        self.api = Flask(__name__)

        # init websocket server
        self.wsServer = WSServer(
            port=self.config["websocketserver"]["port"], host=self.config["websocketserver"]["host"])

        # === define api routes ===
        @self.api.route('/init', methods=['GET'])
        def init_route():  # usage: /init?streamtype=vissim&streamid=streamVissim1&templatetype=traffic-json&templateid=substreamVissim1
            # input parameters
            streamType = request.args.get(
                'streamtype', default="sumo", type=str)  # vissim
            streamID = request.args.get(
                'streamid', default="streamSumo1", type=str)  # streamVissim1
            templateType = request.args.get(
                'templatetype', default="traffic-json", type=str)
            # PS: Changed logic for template ids, if no templated id is given load all templates of type and add them to a dictionary
            #templateID=request.args.get('templateid', default = "substreamVissim1", type = str)

            # check if type match with id
            if streamID not in self.config["streams"][streamType]:
                return json.dumps({"error": "stream ID \""+ streamID+"\" does not match with /streams/ids. \""+streamType+"\""}), 400

            # Read all ids and path from streamType in dictionary, this will be give to the player
            templates = {}
            if templateType not in self.config["templates"][templateType]:
                docs = self.config["templates"][templateType]
                for key, val in docs.items():
                    #print(key, ":", val)
                    templates[key] = val
            else:
                return json.dumps({"error": "template type does not match with /templates/types."}), 400
            # if templateID not in self.config["templates"][templateType]:
            #    return json.dumps({"error":"template ID does not match with template type"}), 400

            # load player
            PlayerClass = self.player_class_loader(
                ROOT_PATH+self.config["player"][streamType]["path"], self.config["player"][streamType]["class"])

            # init player
            # self.config["templates"][templateType][templateID]
            self.player = PlayerClass(
                self.config["streams"][streamType][streamID], templates)

            return json.dumps({"websocket_url": "ws://"+self.config["websocketserver"]["host"]+":"+str(self.config["websocketserver"]["port"])}), 200

        @self.api.route('/getkb', methods=['GET'])
        def getkb_route():  # usage: /getkb
            #return json.dumps({"knowledge base": "example"}), 200
            return self.player.getkb()

        @self.api.route('/start', methods=['GET'])
        def start_route():  # usage: /start?frequency=500
            # input parameters
            frequency = request.args.get('frequency', default=500, type=int) # Old 10
            replayBool = request.args.get('replay', default=False, type=lambda v: v.lower() == 'true')
            aggregateBool = request.args.get('aggregate', default=False, type=lambda v: v.lower() == 'true')

            # start broadcast messages from player (using multithreading)
            broadcast_thread = threading.Thread(
                target=self.broadcasting_thread, args=(self.player.start(frequency,replayBool,aggregateBool), ))
            broadcast_thread.start()

            message=""
            if debug_mode==1:
                message+="! Debug mode are on"

            return json.dumps({"message": "success"+message}), 200

        @self.api.route('/stop', methods=['GET'])
        def stop_route():  # usage: /stop
            self.player.stop()
            return json.dumps({"message": "success"}), 200

        @self.api.route('/modify', methods=['GET'])
        def modify_route():
            frequency = request.args.get('frequency', default=500, type=int) # Old 10
            self.player.modify(frequency)
            return json.dumps({"message": "success"}), 200

    def player_class_loader(self, path, class_name):
        return run_path(path)[class_name]

    def broadcasting_thread(self, messages):
        for msg in messages:
            self.wsServer.broadcast(msg)

    def run(self):
        # start websocket server
        self.wsServer.run()

        # start REST API server
        apiThread = threading.Thread(target=self.api.run, args=(
            self.config["restapi"]["host"], self.config["restapi"]["port"], ))
        apiThread.start()
