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
