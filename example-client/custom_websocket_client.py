import websocket
import threading

class WSClient():
    client= None
    
    #default consumer as print out
    comsumer= print
    def __init__(self, url):
        def on_message(ws, data):
            self.consumer(data)

        def on_error(ws, error):
            print(error)

        def on_close(ws):
            print("connection closed!")

        def on_open(ws):
            print("open connection to server successful!")
            
        #by default, set all event as default
        self.client = websocket.WebSocketApp(url,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              on_open = on_open)
        
    def connect(self):
        clientThread=threading.Thread(target=self.client.run_forever)
        clientThread.start()

    def set_consumer_function(self, consumer):
        self.comsumer=comsumer