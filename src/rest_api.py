RELATIVE_ROOT_PATH="./.."
from runpy import run_path
from flask import Flask, json, request, abort
from custom_websocket_server import WSServer
import threading

class RestApi():
    config=None
    
    def __init__(self, config):
        self.config=config
        #init rest api
        self.api = Flask(__name__)
        
        #init websocket server
        self.wsServer = WSServer(port=self.config["websocketserver"]["port"], host=self.config["websocketserver"]["host"])
        
        #=== define api routes ===
        @self.api.route('/init', methods=['GET'])
        def init_route():#usage: /init?streamtype=vissim&streamid=streamVissim1&templatetype=traffic-json&templateid=substreamVissim1
            #input parameters
            streamType=request.args.get('streamtype', default = "vissim", type = str)
            streamID=request.args.get('streamid', default = "streamVissim1", type = str)            
            templateType=request.args.get('templatetype', default = "traffic-json", type = str)
            templateID=request.args.get('templateid', default = "substreamVissim1", type = str)
            
            #check if type match with id
            if streamID not in self.config["streams"][streamType]:
                return json.dumps({"error":"stream ID does not match with stream type"}), 400
            if templateID not in self.config["templates"][templateType]:
                return json.dumps({"error":"template ID does not match with template type"}), 400
            
            #load player
            PlayerClass=self.player_class_loader(RELATIVE_ROOT_PATH+self.config["player"][streamType]["path"], self.config["player"][streamType]["class"])
            
            #init player
            self.player=PlayerClass(self.config["streams"][streamType][streamID], self.config["templates"][templateType][templateID])
            
            return json.dumps({"websocket_url":"ws://"+self.config["websocketserver"]["host"]+":"+str(self.config["websocketserver"]["port"])}), 200

        @self.api.route('/getkb', methods=['GET'])
        def getkb_route(): #usage: /getkb
            return "knowledge base", 200

        @self.api.route('/start', methods=['GET'])
        def start_route(): #usage: /start?frequency=10
            #input parameters
            frequency=request.args.get('frequency', default = 10, type = int)
            
            #start broadcast messages from player (using multithreading)
            broadcast_thread=threading.Thread(target=self.broadcasting_thread, args=(self.player.start(frequency), ))
            broadcast_thread.start()
            
            return json.dumps({"status":"ok"})

        @self.api.route('/stop', methods=['GET'])
        def stop_route(): #usage: /stop    
            self.player.stop()
            return json.dumps({"status":"ok"})

        @self.api.route('/modify', methods=['GET'])
        def modify_route():
            frequency=request.args.get('frequency', default = 10, type = int)
            self.player.modify(frequency)
            return json.dumps({"status":"ok"})
    
    def player_class_loader(self, path, class_name):
        return run_path(path)[class_name]
    
    def broadcasting_thread(self,messages):
        for msg in messages:
            self.wsServer.broadcast(msg)
    
    def run(self):
        self.wsServer.run()
        #self.api.run(host=self.config["restapi"]["host"], port=self.config["restapi"]["port"])
        apiThread=threading.Thread(target=self.api.run, args=(self.config["restapi"]["host"], self.config["restapi"]["port"], ))
        apiThread.start()
            
    