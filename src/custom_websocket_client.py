import websocket
import threading

class WSClient():
    client= None
    def __init__(self, url):
        def on_message(ws, message):
            self.consumer(message)

        def on_error(ws, error):
            print(error)

        def on_close(ws):
            print("connection closed!")

        def on_open(ws):
            print("open connection to server successful!")
            
        self.client = websocket.WebSocketApp(url,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              on_open = on_open)
    def connect(self):
        clientThread=threading.Thread(target=self.client.run_forever)
        clientThread.start()

    def consumer(self, data):
        #TODO: strat comsuming stream data
        print(data)