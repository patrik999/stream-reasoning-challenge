
import threading
import yaml
from rest-api import RestApi


#load config
with open("../config.yaml","r") as f:
    CONFIG=yaml.safe_load(f)

if __name__ == '__main__':
    #init server
    api=RestApi(CONFIG)
    api.run()
    print("done!")
