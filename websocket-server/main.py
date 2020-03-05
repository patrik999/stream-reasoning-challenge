
import threading
import yaml
from websocket-server import WSSerer
from rest-api import RestApi

#load config
with open("../config.yaml","r") as f:
    CONFIG=yaml.safe_load(f)

#init server
api = RestApi(host='0.0.0.0', port=59125)
server = WSSerer(CONFIG["websocketserver"]["port"], host=CONFIG["websocketserver"]["host"])

def runApi():
    api.run()

def runWebsocket():
    server.run_forever()

if __name__ == '__main__':
  apiThread=threading.Thread(target=runApi)
  websocketThread=threading.Thread(target=runWebsocket)
  apiThread.start()
  websocketThread.start()
  apiThread.join()
  websocketThread.join()
  print("exit!")
