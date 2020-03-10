import requests 
from custom_websocket_client import WSClient
import yaml
import sys
import time

def httprequest(url,params):
    response = requests.get(url = url, params = params) 
    return response.status_code, response.json()


def my_consumer(data):
    #TO-DO: setup consumer data here
    print(data)

#load config
with open("../config.yaml","r") as f:
    CONFIG=yaml.safe_load(f)
    
API_URL="http://"+CONFIG["restapi"]["host"]+":"+str(CONFIG["restapi"]["port"])

#1: call api to init player
status_code, httpResult= httprequest(API_URL+"/init",params={"streamtype":"simple"
                                   ,"streamid":"simpleStream"
                                   ,"templatetype":"traffic-json"
                                   ,"templateid":"substreamVissim1"})
print(status_code, httpResult)
if status_code != 200:
    print("error!")
    sys.exit()

#2: client connect to websocket url from the above init response

    
client=WSClient(httpResult["websocket_url"])
client.set_consumer_function(my_consumer)
client.connect()

time.sleep(2) #wait for client connect success

#3: call api to start stream
status_code, httpResult=httprequest(API_URL+"/start",params={"frequency":10})
print(status_code, httpResult)
if status_code != 200:
    print("error! can not start!")
    sys.exit()
    
