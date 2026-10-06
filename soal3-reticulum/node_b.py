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
