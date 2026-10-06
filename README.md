# Tugas-4 Komunikasi pada Sistem Terdistribusi

## Soal 1 — RPC (list bilangan prima)
```
cd soal1-rpc
docker compose up --build --abort-on-container-exit
```
Hasil: `rpc_prima(11) = 2, 3, 5, 7, 11`

## Soal 2 — Message Queueing (MQTT)
```
cd soal2-mqtt
docker compose up -d --build
docker logs mqtt-publisher
docker logs mqtt-subscriber
docker compose down
```
Publisher kirim data sensor dummy tiap 60 detik ke topik `sensor/dummy` via broker mosquitto.

## Soal 3 — Reticulum Announce
```
cd soal3-reticulum
docker compose up -d --build
docker logs rns-node-a
docker logs rns-node-b
docker compose down
```
Node A announce, Node B menerima dan menampilkan announce.

## Production — Caddy + domain

Service gabung network `vikunja_default` (external), Caddy existing yang pegang 80/443.

`/home/repo/vikunja/Caddyfile`:
```
rpc.devstacklabs.net {
	reverse_proxy rpc-prima-server:8000
}
mqtt.devstacklabs.net {
	reverse_proxy mqtt-broker:9001
}
```

Deploy:
```
cd soal1-rpc && docker compose up -d --build
cd ../soal2-mqtt && docker compose up -d --build
docker exec vikunja-caddy-1 caddy reload --config /etc/caddy/Caddyfile
```

Tes:
```
python3 -c "import xmlrpc.client; print(xmlrpc.client.ServerProxy('https://rpc.devstacklabs.net').rpc_prima(11))"
# rpc_prima(11) = [2, 3, 5, 7, 11]
```
MQTT via WSS (port 443, path `/`, TLS):
```python
import paho.mqtt.client as mqtt
c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
c.ws_set_options(path="/"); c.tls_set()
c.connect("mqtt.devstacklabs.net", 443, 30)
```
