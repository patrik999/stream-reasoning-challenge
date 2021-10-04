# Stream Reasoning Hackathon 2021

Official repository of the Stream Reasoning Challenge 2021,
part of the [Stream Reasoning Workshop 2021](http://streamreasoning.org/events/srw2021).

All the details of the hackathon are given in the [overview document](SR_Hackaton_2021.pdf).

## USAGE

### Requirements

Install docker on your system: https://docs.docker.com/get-docker/

### Server side

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
run `docker-compose up --build`
```

### Server API

Stream generation needs first to be initialized, then a new stream can be (re-)started, stopped, and the update frequency modified.
The following is a list of possible REST-API calls:

-   Initialize stream generation: `http://0.0.0.0:8888/init?streamtype=TYPE&streamid=STREAMID&templatetype=TEMPLATE`

    -   Where `TYPE` has to be replaced with the type of stream. Current support are `sumo` and `perceptionstream`
    -   Where `STREAMID` has to be replaced with the stream ID. For TYPE `sumo`, currently has `streamSumo1`, `streamSumo2` and `streamSumo3`. For TYPE `perceptionstream`, currently has `stream1`, `stream2`, `stream3`, `stream4` and `stream5`.
    -   Where `TEMPLATE` has to be replaced by the output format of send messages. For `sumo`, currently `traffic-json`, `traffic-nt`,
        and `traffic-asp` are choosable. For `perceptionstream`, currently `perceptionstream-n3` and `perceptionstream-nt` are chooseable.

-   Start stream generation: `http://0.0.0.0:8888/start?frequency=500&replay=true`

-   Modify update frequency of a stream: `http://0.0.0.0:8888/modify?frequency=250`

-   Stop stream generation: `http://0.0.0.0:8888/stop`

Note that the arguments in `http://0.0.0.0:8888/init` correspond to keys in `config.yaml`.

Here is an example for the initialization and start of a SUMO traffic stream that sends RDF messages in JSON:

`http://0.0.0.0:8888/init?streamtype=sumo&templatetype=traffic-json`, then
`http://0.0.0.0:8888/start?frequency=500&replay=true`

-   For calling API, there is few ways:
    -   Call by using `curl` in Command Line Interface: `curl --request GET "<url>"`
    -   Open <url> on a browser.
    -   Call by using programming language library such as Python, Java.

### Client side

You should develop your own client using our **REST API** for triggering events such as **init**, **start**, **stop**. Bellow is our example for a basic client, you could modify this example to meet your need.

1. Install dependencies:

```shell
python3 -m pip install websocket-client requests pyyaml
```

2. Go to folder `example-client` and run:

```shell
python3 client.py
```
