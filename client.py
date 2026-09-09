class WoundWaitLockManager:
    """Strict 2PL with Wound-Wait Deadlock Prevention."""
    def __init__(self):
        self.lock_table = {}
        self.tx_timestamps = {}
        self.tx_locks = {}
        self.aborted = set()

    def register_tx(self, tx_id, timestamp):
        self.tx_timestamps[tx_id] = timestamp
        self.tx_locks[tx_id] = set()

    def acquire_lock(self, tx_id, resource, mode='X'):
        if tx_id in self.aborted:
            return {'status': 'ABORTED', 'reason': 'Tx already aborted'}

        t_ts = self.tx_timestamps[tx_id]

        if resource not in self.lock_table:
            self.lock_table[resource] = {'holders': {}, 'waiting': []}

        holders = self.lock_table[resource]['holders']

        conflict = False
        if holders:
            if mode == 'X' or any(h_mode == 'X' for h_mode in holders.values()):
                conflict = True

        if not conflict:
            holders[tx_id] = mode
            self.tx_locks[tx_id].add((resource, mode))
            return {'status': 'GRANTED'}

        holders_to_wound = []
        for h_id in list(holders.keys()):
            if h_id == tx_id:
                continue
            h_ts = self.tx_timestamps[h_id]
            if t_ts < h_ts:
                holders_to_wound.append(h_id)

        if holders_to_wound:
            for h_id in holders_to_wound:
                self.abort_tx(h_id)
            holders = self.lock_table[resource]['holders']
            if not holders or (mode == 'S' and all(m == 'S' for m in holders.values())):
                holders[tx_id] = mode
                self.tx_locks[tx_id].add((resource, mode))
                return {'status': 'GRANTED', 'wounded': holders_to_wound}
            else:
                self.lock_table[resource]['waiting'].append({'tx_id': tx_id, 'mode': mode, 'ts': t_ts})
                return {'status': 'WAITING', 'wounded': holders_to_wound}
        else:
            self.lock_table[resource]['waiting'].append({'tx_id': tx_id, 'mode': mode, 'ts': t_ts})
            return {'status': 'WAITING'}

    def release_locks(self, tx_id):
        for resource, mode in self.tx_locks.get(tx_id, set()):
            if resource in self.lock_table and tx_id in self.lock_table[resource]['holders']:
                del self.lock_table[resource]['holders'][tx_id]
                waiting = self.lock_table[resource]['waiting']
                if waiting:
                    nxt = waiting.pop(0)
                    self.lock_table[resource]['holders'][nxt['tx_id']] = nxt['mode']
                    self.tx_locks[nxt['tx_id']].add((resource, nxt['mode']))
        self.tx_locks[tx_id] = set()

    def abort_tx(self, tx_id):
        self.aborted.add(tx_id)
        self.release_locks(tx_id)
