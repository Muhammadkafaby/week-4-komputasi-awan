# CAK3EAB3 KOMPUTASI AWAN DAN TERDISTRIBUSI

## Tugas-4

### KOMUNIKASI PADA SISTEM TERDISTRIBUSI

Kelompok: Devstack
KELAS IFX-49-01
Dosen: XXX

PROGRAM STUDI XXX
FAKULTAS INFORMATIKA
UNIVERSITAS TELKOM
BANDUNG
2026

---

## Ketentuan

1. Dikerjakan secara kelompok.
2. Dikerjakan langsung pada lembar soal.
3. Jawaban ditulis dengan tulisan tangan yang rapi.
4. Tulisan tangan harus terbaca dengan baik. Tulisan yang tidak terbaca diberi nilai 0.
5. Untuk soal perhitungan, maka cara atau langkah pengerjaan wajib dituliskan.
6. Setiap anggota kelompok wajib mengerjakan soal (ikut berkontribusi).
7. Anggota kelompok yang tidak ikut mengerjakan maka nilainya nol, nama mahasiswa tersebut tidak perlu ditulis di tabel.
8. Unggah jawaban ke LMS diwakili oleh salah satu anggota kelompok. Lembar fisik dikumpulkan pada saat pertemuan di kelas.
9. Lengkapi tabel pernyataan di bawah ini sebagai syarat nilai diinput.

## PERNYATAAN

Saya menyatakan bahwa saya:
(a) benar-benar ikut mengerjakan soal
(b) telah menjelaskan jawaban saya ke teman anggota kelompok
(c) telah memahami penjelasan dari teman anggota kelompok
(d) tidak mencontek jawaban dari kelompok lain
(e) tidak memberikan jawaban PR ini ke kelompok lain

| Nama | NIM | Kontribusi Tugas | Tanda Tangan |
|------|-----|------------------|--------------|
| Muhammad Kafaby | 103012580045 | Soal 1 (RPC) | |
| Davi Pramudya Putra | 103012580056 | Soal 2 (Message Queueing) | |
| Dzaki Alwan Fitjatullah | 103012580006 | Soal 3 (Reticulum Announce) | |
| M. Faishal Rafid | 103012580034 | Deployment Caddy + dokumentasi | |

---

# TUGAS 4

## 1. RPC (Remote Procedure Call)

### Soal

1. Buatlah program sederhana menggunakan RPC!
2. Server mempunyai sebuah service/fungsi yaitu mengembalikan list bilangan prima. Parameter fungsi adalah batas terbesar angka. Contoh `rpc_prima(11)` maka hasilnya adalah 2, 3, 5, 7, 11.
3. Client meminta service/fungsi yang ada pada server menggunakan RPC.
4. Masukkan program/service pada container dan pastikan service pada container bisa diakses. Screenshot hasilnya.

### Jawaban

RPC dibuat memakai **XML-RPC** (pustaka standar Python `xmlrpc`). Server mengekspos fungsi `rpc_prima(batas)` yang mengembalikan seluruh bilangan prima `<= batas` menggunakan algoritma **Sieve of Eratosthenes**.

**Alur kerja:**

1. Server mendaftarkan fungsi `rpc_prima` pada `SimpleXMLRPCServer` dan listen di port `8000`.
2. Client membuka `ServerProxy` ke server, lalu memanggil `rpc_prima(11)` seperti memanggil fungsi lokal.
3. Server menghitung bilangan prima dan mengirim balik hasilnya via HTTP.

**Kode server** (`soal1-rpc/prima_server.py`):

```python
from xmlrpc.server import SimpleXMLRPCServer


def rpc_prima(batas):
    """Kembalikan list bilangan prima <= batas."""
    if batas < 2:
        return []
    sieve = [True] * (batas + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(batas ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, batas + 1, i):
                sieve[j] = False
    return [n for n, ok in enumerate(sieve) if ok]


if __name__ == "__main__":
    server = SimpleXMLRPCServer(("0.0.0.0", 8000), allow_none=True)
    server.register_function(rpc_prima, "rpc_prima")
    print("RPC server prima jalan di 0.0.0.0:8000", flush=True)
    server.serve_forever()
```

**Kode client** (`soal1-rpc/prima_client.py`):

```python
import sys
import xmlrpc.client

host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
batas = int(sys.argv[2]) if len(sys.argv) > 2 else 11

proxy = xmlrpc.client.ServerProxy(f"http://{host}:8000")
hasil = proxy.rpc_prima(batas)
print(f"rpc_prima({batas}) = {', '.join(map(str, hasil))}", flush=True)
```

**Langkah pengerjaan (perhitungan):**

Untuk `rpc_prima(11)`:

1. Buat tabel boolean `0..11`, tandai `0` dan `1` bukan prima.
2. `i = 2` (2² = 4 ≤ 11): tandai kelipatan 2 → 4, 6, 8, 10 bukan prima.
3. `i = 3` (3² = 9 ≤ 11): tandai kelipatan 3 → 6, 9 bukan prima.
4. `i = 4` (4² = 16 > 11): berhenti.
5. Sisa yang bertanda prima: **2, 3, 5, 7, 11**.

**Cara menjalankan (container):**

```bash
cd soal1-rpc
docker compose up --build --abort-on-container-exit
```

**Hasil:**

```
rpc-prima-server  | RPC server prima jalan di 0.0.0.0:8000
rpc-prima-client  | rpc_prima(11) = 2, 3, 5, 7, 11
```

> **[Screenshot: output client `rpc_prima(11) = 2, 3, 5, 7, 11`]**

---

## 2. Message Queueing

### Soal

1. Buatlah satu program sederhana menggunakan metode message queueing (MQTT / RabbitMQ / ZeroMQ).
2. Buat program yang mengirimkan data hasil sensor (dummy) secara periodik (program mengirim data dummy setiap 1 menit sekali ke program lain).
3. Masukkan program/service pada container dan pastikan service pada container bisa diakses. Screenshot hasilnya.

### Jawaban

Message queueing dibuat memakai **MQTT** (broker `eclipse-mosquitto`, pustaka client `paho-mqtt`). Terdapat tiga komponen:

1. **Broker** (`mosquitto`) — perantara pesan, listen port `1883`.
2. **Publisher** — mengirim data sensor dummy tiap **60 detik** ke topik `sensor/dummy`.
3. **Subscriber** — subscribe topik `sensor/dummy` dan menampilkan data yang diterima.

**Kode publisher** (`soal2-mqtt/publisher.py`):

```python
import json
import os
import random
import time

import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
INTERVAL = int(os.getenv("INTERVAL", "60"))
TOPIC = "sensor/dummy"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, 1883, 60)
client.loop_start()

print(f"Publisher kirim data sensor dummy tiap {INTERVAL} detik ke topik '{TOPIC}'", flush=True)
while True:
    data = {
        "suhu": round(random.uniform(25, 35), 2),
        "kelembapan": round(random.uniform(40, 80), 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    client.publish(TOPIC, json.dumps(data))
    print("kirim:", data, flush=True)
    time.sleep(INTERVAL)
```

**Kode subscriber** (`soal2-mqtt/subscriber.py`):

```python
import os

import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
TOPIC = "sensor/dummy"


def on_connect(client, userdata, flags, rc, props=None):
    print(f"Subscriber terhubung ke broker {BROKER}, subscribe '{TOPIC}'", flush=True)
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    print(f"terima [{msg.topic}] {msg.payload.decode()}", flush=True)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_forever()
```

**Konfigurasi broker** (`soal2-mqtt/mosquitto.conf`):

```conf
listener 1883
protocol mqtt
allow_anonymous true

listener 9001
protocol websockets
allow_anonymous true
```

**Cara menjalankan (container):**

```bash
cd soal2-mqtt
docker compose up -d --build
docker logs mqtt-publisher
docker logs mqtt-subscriber
```

**Hasil** (publisher kirim tiap 60 detik, subscriber menerima):

```
mqtt-publisher   | Publisher kirim data sensor dummy tiap 60 detik ke topik 'sensor/dummy'
mqtt-publisher   | kirim: {'suhu': 32.9, 'kelembapan': 48.85, 'timestamp': '2026-10-06 07:02:12'}
mqtt-publisher   | kirim: {'suhu': 29.29, 'kelembapan': 57.42, 'timestamp': '2026-10-06 07:03:12'}
mqtt-subscriber  | Subscriber terhubung ke broker mosquitto, subscribe 'sensor/dummy'
mqtt-subscriber  | terima [sensor/dummy] {"suhu": 29.29, "kelembapan": 57.42, "timestamp": "2026-10-06 07:03:12"}
```

> **[Screenshot: log publisher dan subscriber]**

---

## 3. Reticulum Announce

### Soal

Buatlah program sederhana menggunakan reticulum yang bisa melakukan announce. Node A melakukan announce dan node B menerima announce tersebut kemudian menampilkannya.

### Jawaban

Dibuat dua node memakai pustaka **Reticulum (RNS)** yang saling terhubung lewat **TCP Interface** (Node A sebagai TCP server, Node B sebagai TCP client). Node A membuat `Destination` dan memanggil `announce()`, Node B mendaftarkan **announce handler** untuk menerima dan menampilkan announce.

**Kode Node A** (`soal3-reticulum/node_a.py`):

```python
import os
import time

import RNS

CONFIGDIR = os.getenv("RNS_CONFIG", "/root/.reticulum")

CONFIG = """[reticulum]
  enable_transport = No
  share_instance = No
  panic_on_interface_error = No

[logging]
  loglevel = 4

[interfaces]
  [[TCP Server]]
    type = TCPServerInterface
    interface_enabled = True
    listen_ip = 0.0.0.0
    listen_port = 4242
"""


def write_config():
    os.makedirs(CONFIGDIR, exist_ok=True)
    path = os.path.join(CONFIGDIR, "config")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(CONFIG)


write_config()
RNS.Reticulum(configdir=CONFIGDIR)

identity = RNS.Identity()
dest = RNS.Destination(
    identity, RNS.Destination.IN, RNS.Destination.SINGLE, "tugas", "announce"
)

print("Node A siap. Destination hash:", dest.hexhash, flush=True)
while True:
    dest.announce(app_data=b"halo dari node A")
    print("Node A mengirim announce:", dest.hexhash, flush=True)
    time.sleep(15)
```

**Kode Node B** (`soal3-reticulum/node_b.py`):

```python
import os
import time

import RNS

CONFIGDIR = os.getenv("RNS_CONFIG", "/root/.reticulum")

CONFIG = """[reticulum]
  enable_transport = No
  share_instance = No
  panic_on_interface_error = No

[logging]
  loglevel = 4

[interfaces]
  [[TCP Client]]
    type = TCPClientInterface
    interface_enabled = True
    target_host = node_a
    target_port = 4242
"""


def write_config():
    os.makedirs(CONFIGDIR, exist_ok=True)
    path = os.path.join(CONFIGDIR, "config")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(CONFIG)


write_config()
RNS.Reticulum(configdir=CONFIGDIR)


class AnnounceHandler:
    aspect_filter = "tugas.announce"

    def received_announce(self, destination_hash, announced_identity, app_data):
        print("Node B menerima announce:", RNS.hexrep(destination_hash, delimit=False), flush=True)
        if app_data:
            print("  app_data:", app_data.decode(errors="replace"), flush=True)


RNS.Transport.register_announce_handler(AnnounceHandler())
print("Node B menunggu announce dari node A...", flush=True)
while True:
    time.sleep(1)
```

**Catatan:** `register_announce_handler` hanya menerima handler yang punya atribut `aspect_filter`, sehingga handler Node B wajib mendefinisikan `aspect_filter`.

**Cara menjalankan (container):**

```bash
cd soal3-reticulum
docker compose up -d --build
docker logs rns-node-a
docker logs rns-node-b
```

**Hasil:**

```
rns-node-a  | Node A siap. Destination hash: 1914016191ac77c5b5660846f8bbb646
rns-node-a  | Node A mengirim announce: 1914016191ac77c5b5660846f8bbb646
rns-node-b  | Node B menunggu announce dari node A...
rns-node-b  | Node B menerima announce: 1914016191ac77c5b5660846f8bbb646
rns-node-b  |   app_data: halo dari node A
```

> **[Screenshot: log Node A mengirim announce dan Node B menerima announce]**

---

## Lampiran — Deployment Production (Caddy + Domain)

Ketiga service di-deploy pada satu host dan diakses lewat domain menggunakan **Caddy** sebagai reverse proxy dengan TLS otomatis (Let's Encrypt).

**Domain & DNS:**

| Domain | Tipe | Arah | Service |
|--------|------|------|---------|
| `rpc.devstacklabs.net` | A | `43.157.210.87` | RPC server (`rpc-prima-server:8000`) |
| `mqtt.devstacklabs.net` | A | `43.157.210.87` | MQTT WebSocket (`mqtt-broker:9001`) |
| `kanban.devstacklabs.net` | A | `43.157.210.87` | Vikunja (existing) |

**Network:** service RPC & MQTT digabung ke network `vikunja_default` (external) agar dapat di-resolve oleh Caddy yang sudah berjalan.

**Caddyfile** (`/home/repo/vikunja/Caddyfile`):

```
kanban.devstacklabs.net {
	reverse_proxy vikunja:3456
}

rpc.devstacklabs.net {
	reverse_proxy rpc-prima-server:8000
}

mqtt.devstacklabs.net {
	reverse_proxy mqtt-broker:9001
}
```

MQTT diekspos melalui **WebSocket** (listener `9001`) karena Caddy `reverse_proxy` mendukung WebSocket secara native, sehingga tidak perlu build plugin `caddy-l4` untuk TCP mentah.

**Deploy:**

```bash
cd soal1-rpc && docker compose up -d --build
cd ../soal2-mqtt && docker compose up -d --build
docker exec vikunja-caddy-1 caddy reload --config /etc/caddy/Caddyfile
```

**Verifikasi:**

```bash
python3 -c "import xmlrpc.client; print(xmlrpc.client.ServerProxy('https://rpc.devstacklabs.net').rpc_prima(11))"
# rpc_prima(11) = [2, 3, 5, 7, 11]
```

```python
import paho.mqtt.client as mqtt
c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
c.ws_set_options(path="/")
c.tls_set()
c.connect("mqtt.devstacklabs.net", 443, 30)
```

**Hasil:**

```
https://rpc.devstacklabs.net   → rpc_prima(11) = [2, 3, 5, 7, 11]
wss://mqtt.devstacklabs.net/   → terima [sensor/dummy] {"suhu":30.98,...}
https://kanban.devstacklabs.net → 200
```

> **[Screenshot: akses `https://rpc.devstacklabs.net` dan client MQTT via `wss://mqtt.devstacklabs.net`]**

**Catatan keamanan:** `allow_anonymous true` pada broker hanya untuk demo; untuk production wajib diaktifkan autentikasi (user/password atau client certificate) beserta ACL.
