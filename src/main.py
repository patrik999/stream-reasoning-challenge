import threading
import yaml
from rest_api import RestApi
import requests 
from custom_websocket_client import WSClient
import time

#load config
with open("../config.yaml","r") as f:
    CONFIG=yaml.safe_load(f)

    
def httprequest(url,params):
    r = requests.get(url = url, params = params) 
    return r.json()
    
if __name__ == '__main__':
    #init server
    api=RestApi(CONFIG)
    api.run()
    
    
    API_URL="http://"+CONFIG["restapi"]["host"]+":"+str(CONFIG["restapi"]["port"])
    #1: call api to init player
    httpResult=httprequest(API_URL+"/init",params={"streamtype":"simple"
                                       ,"streamid":"simpleStream"
                                       ,"templatetype":"traffic-json"
                                       ,"templateid":"substreamVissim1"})
    print(httpResult)
    #2: client connect to websocket url from the above init response
    client=WSClient(httpResult["websocket_url"])
    client.connect()
    
    #3: call api to start stream
    httpResult=httprequest(API_URL+"/start",params={"frequency":10})
    
    
    
    