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
