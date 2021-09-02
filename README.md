# Stream Reasoning Challenge 2020

Official repository of the Stream Reasoning Challengee 2020, 
part of the Stream Reasoning Workshop 2020 ()


## USAGE

### Server side
1. Clone this git
```
git clone https://github.com/patrik999/stream-reasoning-challenge.git
```

2. Launch system in docker
```
docker run -it --rm\
    --env="DISPLAY" \
    --volume="/etc/group:/etc/group:ro" \
    --volume="/etc/passwd:/etc/passwd:ro" \
    --volume="/etc/shadow:/etc/shadow:ro" \
    --volume="/etc/sudoers.d:/etc/sudoers.d:ro" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --user=$USER \
    -p 59125:59125 \
    -p 59126:59126 \
    docker-sumo \
    bash
```
<!--2. Modify host and port for REST API and websocket server in ```config.yaml```
3. Modify the expose ports in ```docker-compose.yml``` to matching with the ports you has modified in ```config.yaml```
3. Run server using docker compose
```
docker-compose up
```
**Note**: To apply any change to server code, please run ```docker-compose up --build```
-->
### Client side
go to folder ```example-client``` and run 
```
python3 client.py
```
