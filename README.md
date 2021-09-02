# Stream Reasoning Challenge 2020

Official repository of the Stream Reasoning Challengee 2020,
part of the Stream Reasoning Workshop 2020 ()

## USAGE

### Server side

1. Clone this git

```
git clone https://github.com/patrik999/stream-reasoning-challenge.git
cd stream-reasoning-challenge
```

2. The **host** and **port** for the **REST API** and the **WebSocket server** are set in the `config.yaml` file. You could change it to another host and port.
3. If you have modified the **port** in the `config.yaml`, you should change the expose ports in the `docker-compose.yml` too.
4. Launch the server using `docker-compose` by run the following command (the first run will take some time for the system build, from the next runs, it will get up faster):

```
docker-compose up
```

Once you see the output as below, it means the server are ready!

> INFO:werkzeug: \* Running on http://172.18.0.2:59125/ (Press CTRL+C to quit)

**Note**: For any modify in the server code, please run `docker-compose up --build` to rebuild the system.

### Client side

1. Install dependencies:

```
python3 -m pip install websocket-client requests
```

2. Go to folder `example-client` and run:

```
python3 client.py
```
