# client.py
import socket, struct, time

HOST = "127.0.0.1"
PORT = 1234

# ---- Protocol helpers -------------------------------------------------
# Request:  [4B n_args][ [4B len][bytes] ... ]
# Framed by: [4B total_len_of_payload]
def pack_req(args):
    payload = struct.pack("<I", len(args))
    for a in args:
        b = a.encode("utf-8")
        payload += struct.pack("<I", len(b)) + b
    return struct.pack("<I", len(payload)) + payload  # outer frame

def recv_exact(sock, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("server closed connection")
        buf += chunk
    return bytes(buf)

def recv_resp(sock):
    # Response is also framed: [4B len][payload...]
    hdr = recv_exact(sock, 4)
    (ln,) = struct.unpack("<I", hdr)
    return recv_exact(sock, ln)  # raw payload (type-tagged by server)

# Optional: minimal, generic pretty-printer for common types
def parse_and_print(resp):
    if not resp:
        print("(empty)")
        return
    tag = resp[0]
    body = resp[1:]
    # These tag numbers are typical for this project; it's okay if unknown.
    SER_NIL, SER_ERR, SER_STR, SER_INT, SER_DBL, SER_ARR = 0, 1, 2, 3, 4, 5
    try:
        if tag == SER_NIL:
            print("(nil)")
        elif tag == SER_ERR:
            code = struct.unpack("<I", body[:4])[0]
            slen = struct.unpack("<I", body[4:8])[0]
            msg = body[8:8+slen].decode("utf-8", "replace")
            print(f"(error {code}) {msg}")
        elif tag == SER_STR:
            slen = struct.unpack("<I", body[:4])[0]
            s = body[4:4+slen].decode("utf-8", "replace")
            print(s)
        elif tag == SER_INT:
            val = struct.unpack("<q", body[:8])[0]
            print(val)
        elif tag == SER_DBL:
            val = struct.unpack("<d", body[:8])[0]
            print(val)
        elif tag == SER_ARR:
            n = struct.unpack("<I", body[:4])[0]
            print(f"(array of {n} items, raw={resp.hex()})")
        else:
            print(f"(unknown tag {tag}, raw={resp.hex()})")
    except Exception:
        print(f"(could not parse, raw={resp.hex()})")

# ---- Simple interactive demo ------------------------------------------
def demo():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        for args in [
            ["set", "foo", "bar"],
            ["get", "foo"],
            ["zadd", "myz", "1.5", "alice"],
            ["zscore", "myz", "alice"],
            ["keys"],
        ]:
            s.sendall(pack_req(args))
            resp = recv_resp(s)
            print("> ", " ".join(args))
            parse_and_print(resp)

# ---- Benchmark: reuse one connection ----------------------------------
def benchmark(n=10000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        start = time.time()
        for i in range(n):
            s.sendall(pack_req(["set", f"key{i}", str(i)]))
            _ = recv_resp(s)  # ignore content, but fully read it
        dur = time.time() - start
        print(f"Sent {n} requests in {dur:.3f}s ({n/dur:,.0f} req/sec)")

if __name__ == "__main__":
    print("Running demo…")
    demo()
    print("\nRunning benchmark…")
    benchmark(1000)
