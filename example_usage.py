from client import WoundWaitLockManager

def main():
    print("=== Testing Wound-Wait Two-Phase Locking ===")
    mgr = WoundWaitLockManager()
    # T1 older (ts=100), T2 younger (ts=200)
    mgr.register_tx(1, 100)
    mgr.register_tx(2, 200)

    res1 = mgr.acquire_lock(2, "table_users", 'X')
    print("T2 acquires lock:", res1)
    assert res1['status'] == 'GRANTED'

    # Older T1 requests table_users -> wounds younger T2
    res2 = mgr.acquire_lock(1, "table_users", 'X')
    print("T1 acquires lock (wounding T2):", res2)
    assert res2['status'] == 'GRANTED'
    assert 2 in mgr.aborted
    print("Wound-Wait 2PL verified successfully!")

if __name__ == '__main__':
    main()
