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

### Server API

Stream generation needs first to be initalized, then a new stream can be (re-)started, stopped, and the update frequency modified.
The following is a list of possible REST-API calls:

- Initialize stream generation: `/init?streamtype=TYPE&templatetype=TEMPLATE`,
where `TYPE` has to be replaced with the type of stream, currently `sumo` is provided, `TEMPLATE`
has to be replaced by the output format of send messages, currently `traffic-json`, `traffic-nt`,
and `traffic-asp` are choosable.

- Start stream generation: `/start`

- Modify update frequency of a stream: `/modify?frequency=0.1`

- Stop stream generation: `/stop`

Note that the values arguments in  `/init` correspond to keys in `config.yaml`.
Here an example for the initialization and start of a SUMO traffic stream that sends RDF message in JSON:

`http://192.168.0.206:59125/init?streamtype=sumo&templatetype=traffic-json`, then
`http://192.168.0.206:59125/start`


### Client side

You should develope your own client using our **REST API** for trigger events such as **init**, **start**, **stop**. Bellow are our example for a basic client, you could modify this example to meet your need.

1. Install dependencies:

```
python3 -m pip install websocket-client requests
```

2. Go to folder `example-client` and run:

```
python3 client.py
```
