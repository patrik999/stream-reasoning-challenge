# Stream Reasoning Challenge 2020

Official repository of the Stream Reasoning Challengee 2020, 
part of the Stream Reasoning Workshop 2020 ()


## USAGE

### Server side
1. Clone this git
```
git clone https://github.com/patrik999/stream-reasoning-challenge.git
```

2. Modify host and port for REST API and websocket server in ```config.yaml```
3. Modify the expose ports in ```docker-compose.yml``` to matching with the ports you has modified in ```config.yaml```
3. Run server using docker compose
```
docker-compose up
```

### Client side
go to folder ```example-client``` and run 
```
python3 client.py
```
