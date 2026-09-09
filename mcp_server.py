import sys
import json
from client import WoundWaitLockManager

def handle_request(req):
    method = req.get("method")
    params = req.get("params", {})
    if method == "test_wound_wait":
        mgr = WoundWaitLockManager()
        mgr.register_tx(1, 10)
        mgr.register_tx(2, 20)
        mgr.acquire_lock(2, "R1", "X")
        res = mgr.acquire_lock(1, "R1", "X")
        return {"result": res, "aborted": list(mgr.aborted)}
    return {"error": "Unknown method"}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line)
        res = handle_request(req)
        print(json.dumps(res))
        sys.stdout.flush()

if __name__ == '__main__':
    main()
