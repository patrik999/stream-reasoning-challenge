from websocket_server import WebsocketServer


class WSServer():
    def __init__(self, port, host):
        self.server = WebsocketServer(port, host=host)
        server.set_fn_new_client(self.new_client)
        server.set_fn_client_left(self.close_connection)

    def new_client(self, client, _server):
        print("client connected", client)

    def close_connection(self, client,_server):
        print(client,"disconnected")

    def run(self):
        self.server.run_forever()