import sys
import xmlrpc.client

host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
batas = int(sys.argv[2]) if len(sys.argv) > 2 else 11

proxy = xmlrpc.client.ServerProxy(f"http://{host}:8000")
hasil = proxy.rpc_prima(batas)
print(f"rpc_prima({batas}) = {', '.join(map(str, hasil))}", flush=True)
