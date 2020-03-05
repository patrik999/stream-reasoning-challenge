from flask import Flask, json, request
from websocket_server import WebsocketServer
from datetime import datetime
import time
import threading

clients=[]
api = Flask(__name__)
server = WebsocketServer(59126, host='0.0.0.0')

#======== websocket functions ===========
def new_client(client, _server):
  print("client connected",client)
  clients.append(client)

def close_connection(client,_server):
  print(client,"disconnected")
  clients.remove(client)
  print(clients)

server.set_fn_new_client(new_client)
server.set_fn_client_left(close_connection)


#===== API ======
@api.route('/init', methods=['GET'])
def init():
  streamID=request.args.get('streamid', default = 1, type = int)
  templateID=request.args.get('templateid', default = 1, type = int)
  result={"StreamID":streamID,"templateID":templateID}
  #TO-DO: initialize stream player

  return json.dumps(result)

@api.route('/getkb', methods=['GET'])
def getkb():
  with open("kb.txt","r") as f:
    kb=f.read()
  return kb

@api.route('/start', methods=['GET'])
def start():
  frequency=request.args.get('frequency', default = 1, type = int)
  #start player
  return json.dumps({"status":"ok"})

@api.route('/stop', methods=['GET'])
def stop():        
  #stop player
  return json.dumps({"status":"ok"})

@api.route('/mod', methods=['GET'])
def modify():
  frequency=request.args.get('frequency', default = 1, type = int)
  #modify player freq
  return json.dumps({"status":"ok"})

def runApi():
  api.run(host='0.0.0.0', port=59125)

def runWebsocket():
  try:
    server.run_forever()
  except:
    pass

if __name__ == '__main__':
  apiThread=threading.Thread(target=runApi)
  websocketThread=threading.Thread(target=runWebsocket)
  apiThread.start()
  websocketThread.start()
  apiThread.join()
  websocketThread.join()
  print("exit!")
