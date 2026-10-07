#!/usr/bin/env bash
# Capture hasil nyata tiap soal lalu render jadi PNG gaya terminal.
# Pakai ImageMagick (convert) + font DejaVu Sans Mono. Tanpa dependency baru.
set -uo pipefail
cd "$(dirname "$0")/.."
OUT=screenshots
mkdir -p "$OUT"
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf
POINT=15

shot() {
  local name="$1"
  local txt
  txt=$(cat)
  local maxlen
  maxlen=$(printf '%s\n' "$txt" | awk '{ if (length > m) m = length } END { print m+1 }')
  local w=$(( maxlen * 10 + 40 ))
  printf '%s\n' "$txt" > "$OUT/$name.txt"
  # escape % agar tidak diinterpret ImageMagick sebagai properti
  local esc=${txt//%/%%}
  convert -background '#1e1e1e' -fill '#e6e6e6' -font "$FONT" -pointsize "$POINT" \
    -gravity northwest -size "${w}x" caption:"$esc" \
    -bordercolor '#1e1e1e' -border 16 "$OUT/$name.png"
  echo "  -> $OUT/$name.png ($(identify -format '%wx%h' "$OUT/$name.png"))"
}

P='user@devstack:~/week-4-komputasi-awan'

echo "[1] RPC"
RPC=$(cd soal1-rpc && docker compose up --build --abort-on-container-exit 2>&1 \
  | grep -E 'rpc-prima-(server|client)  \|' || true)
shot 01-rpc <<EOF
$P/soal1-rpc\$ docker compose up --build --abort-on-container-exit
$RPC
EOF
# server dihidupkan lagi (tadi ikut berhenti) agar akses https://rpc.devstacklabs.net siap
(cd soal1-rpc && docker compose up -d server >/dev/null 2>&1)
sleep 3

echo "[2] MQTT"
PUB=$(docker logs --tail 3 mqtt-publisher 2>&1)
SUB=$(docker logs --tail 2 mqtt-subscriber 2>&1)
shot 02-mqtt <<EOF
user@devstack:~\$ docker logs mqtt-publisher
$PUB
user@devstack:~\$ docker logs mqtt-subscriber
$SUB
EOF

echo "[3] Reticulum"
NA=$(docker logs rns-node-a 2>&1 | grep -E 'Node A' | head -3)
NB=$(docker logs rns-node-b 2>&1 | grep -E 'Node B|app_data' | head -3)
shot 03-reticulum <<EOF
user@devstack:~\$ docker logs rns-node-a
$NA
user@devstack:~\$ docker logs rns-node-b
$NB
EOF

echo "[4] Deployment"
RPC1=$(python3 -c "import xmlrpc.client; print(xmlrpc.client.ServerProxy('https://rpc.devstacklabs.net').rpc_prima(11))" 2>&1)
KAN=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 https://kanban.devstacklabs.net)
WSS=$(docker run --rm --network vikunja_default --entrypoint python soal2-mqtt-publisher -c "
import paho.mqtt.client as mqtt
def on_connect(c,u,f,rc,p=None):
    print('CONNECT rc=', rc); c.subscribe('sensor/dummy')
def on_message(c,u,m):
    print('WSS terima [%s] %s' % (m.topic, m.payload.decode())); c.disconnect()
c=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport='websockets')
c.ws_set_options(path='/'); c.tls_set()
c.on_connect=on_connect; c.on_message=on_message
c.connect('mqtt.devstacklabs.net', 443, 30); c.loop_forever()
" 2>&1 | head -2)
shot 04-deploy <<EOF
user@devstack:~\$ python3 -c "import xmlrpc.client; print(xmlrpc.client.ServerProxy('https://rpc.devstacklabs.net').rpc_prima(11))"
$RPC1
user@devstack:~\$ curl -s -o /dev/null -w '%{http_code}' https://kanban.devstacklabs.net
$KAN
user@devstack:~\$ python3 -c "import paho.mqtt.client as mqtt; ... connect wss://mqtt.devstacklabs.net:443"
$WSS
EOF

echo "selesai."
