from flask import Flask, json, request

class RestApi():
    def __init__(self, host, port):
        self.api = Flask(__name__)
        self.host=host
        self.port=port
        @self.api.route('/init', methods=['GET'])
        def init():
          streamID=request.args.get('streamid', default = 1, type = str)
          templateID=request.args.get('templateid', default = 1, type = str)
          #TO-DO: initialize stream player

          return json.dumps({"status":"ok"})

        @self.api.route('/getkb', methods=['GET'])
        def getkb():
          with open("kb.txt","r") as f:
            kb=f.read()
          return kb

        @self.api.route('/start', methods=['GET'])
        def start():
          frequency=request.args.get('frequency', default = 1, type = int)
          #start player
          return json.dumps({"status":"ok"})

        @self.api.route('/stop', methods=['GET'])
        def stop():        
          #stop player
          return json.dumps({"status":"ok"})

        @self.api.route('/mod', methods=['GET'])
        def modify():
          frequency=request.args.get('frequency', default = 1, type = int)
          #modify player freq
          return json.dumps({"status":"ok"})
    
    def run(self):
         self.api.run(self.host, self.port)