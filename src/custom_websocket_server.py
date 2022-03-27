import threading
from websocket_server import WebsocketServer

class WSServer():
    def __init__(self, port, host):
        self.server = WebsocketServer(port=port, host=host)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.close_connection)

    def new_client(self, client, _server):
        print("client connected", client)

    def close_connection(self, client,_server):
        print(client,"disconnected")

    def broadcast(self, message):
        self.server.send_message_to_all(message)

    def run(self):
        serverThread=threading.Thread(target=self.server.run_forever)
        serverThread.start()
