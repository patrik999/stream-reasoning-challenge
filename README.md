# Stream Reasoning Playground

Official repository of the Stream Reasoning Hackathon 2021,
part of the [Stream Reasoning Workshop 2021](http://streamreasoning.org/events/srw2021).

All the details of the 2021 hackathon are given in the [overview document](SR_Hackaton_2021.pdf).

## USAGE

The main idea is to use a server to generate a stream of data and then stream the data to the client through a WebSocket. The server is also acting as a web server to control the server through our provided REST API.

### Requirements

Install Docker on your system as described in: https://docs.docker.com/get-docker/

### Server Setup
To setup the server, you could either choose to use our prebuild docker image for instant test with our standard setup and players or custom and build your own docker image on your local machine.

#### A. Run with prebuild docker image on Docker Hub
1. Pull image to local:
```shell
docker pull manhnguyenduc/stream-reasoning-playground:standard
```

2. Run server:
* _The default port for REST API is 8888 and default port for websocket server is 8889, so we should expose it to host_
```shell
docker run --rm -p 8888:8888 -p 8889:8889 manhnguyenduc/stream-reasoning-playground:standard
```



#### B. Build and run docker image on local machine
1. Clone this git

```shell
git clone https://github.com/patrik999/stream-reasoning-challenge.git
cd stream-reasoning-challenge
```

2. The **host** and **port** for the **REST API** and the **WebSocket server** are set in the `config.yaml` file. You could change it to another host and port.
3. If you have modified the **port** in the `config.yaml`, you should change the expose ports in the `docker-compose.yml` too.
4. Launch the server using `docker-compose` by run the following command (the first run will take some time for the system build, from the next runs, it will get up faster):

```shell
docker-compose up
```

Once you see the output as below, it means the server is ready!

> INFO:werkzeug: \* Running on http://172.18.0.2:8888/ (Press CTRL+C to quit)

**Note**: For any server code modification, rebuild the system by running:

```shell
docker-compose up --build
```

### Server API

Stream generation needs first to be initialized, then a new stream can be (re-)started, stopped, and the update frequency modified.
The following is a list of possible REST-API calls:

_* NOTE: if you are working with Docker on Mac OS or Windows OS platform, please try to replace the address `0.0.0.0` by `localhost` if it is not working_

-   Initialize stream generation: `http://0.0.0.0:8888/init?streamtype=TYPE&streamid=STREAMID&templatetype=TEMPLATE`

    -   Where `TYPE` has to be replaced with the type of stream. Current support are `sumo` and `perceptionstream`
    -   Where `STREAMID` has to be replaced with the stream ID. For TYPE `sumo`, currently has `streamSumo1`, `streamSumo2` and `streamSumo3`. For TYPE `perceptionstream`, currently has `stream1`, `stream2`, `stream3`, `stream4` and `stream5`.
    -   Where `TEMPLATE` has to be replaced by the output format of send messages. For `sumo`, currently `traffic-json`, `traffic-nt`,
        and `traffic-asp` are choosable. For `perceptionstream`, currently `perceptionstream-n3`, `perceptionstream-nt`, `perceptionstream-jsonld` and `perceptionstream-asp` are chooseable.

-   Start stream generation: `http://0.0.0.0:8888/start?frequency=500&replay=true&aggregate=true`
    -  frequency=500 is the update frequency in ms
    -  replay=true states that the stream is running infinitely
    -  aggregate=true states that atomt messagess for one (simulation) step are combined and send as a single message

-   Modify update frequency of a stream: `http://0.0.0.0:8888/modify?frequency=250`

-   Stop stream generation: `http://0.0.0.0:8888/stop`

Note that the arguments in `http://0.0.0.0:8888/init` correspond to keys in `config.yaml`.

Here is an example for the initialization and start of a SUMO traffic stream that sends RDF messages in JSON:

`http://0.0.0.0:8888/init?streamtype=sumo&streamid=streamSumo1&templatetype=traffic-json`, then
`http://0.0.0.0:8888/start?frequency=500&replay=true`

-   To calling the API, there is few ways:
    -   Call by using `curl` in Command Line Interface: `curl --request GET "<url>"`
    -   Open the `<url>` on a browser.
    -   Call by using programming language library such as Python, Java.

### Client Setup

You should develop your own client using our **REST API** for triggering events such as **init**, **start**, **stop**. Bellow is our example for a basic client, you could modify this example to meet your need.

#### Demo Python Client

1. Install dependencies:

```shell
python3 -m pip install websocket-client requests pyyaml
```

2. Go to folder `example-client` and run:

```shell
python3 client.py
```

#### Custom Client

You could develop your own client base on 2 step below:

1. Call the Initialize API from above to get back the Websocket URL, return message is an JSON has format as bellow

```
{"websocket_url": "ws://0.0.0.0:8889"}
```

2. Connect to the websocket above and listen for message from the server.
