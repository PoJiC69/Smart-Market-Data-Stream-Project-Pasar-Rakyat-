"""
Simple blockchain ledger storing hashed price entries for integrity verification.
"""
from __future__ import annotations

import hashlib
import json
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Block:
    index: int
    timestamp: str
    data: Dict
    prev_hash: str
    hash: str

class SimpleLedger:
    def __init__(self):
        self.chain: List[Block] = []
        # create genesis
        genesis = Block(index=0, timestamp="0", data={"genesis": True}, prev_hash="0", hash="0")
        self.chain.append(genesis)

    def add_entry(self, data: Dict) -> Block:
        prev = self.chain[-1]
        idx = prev.index + 1
        timestamp = str(__import__("time").time())
        payload = {"index": idx, "timestamp": timestamp, "data": data, "prev_hash": prev.hash}
        h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        block = Block(index=idx, timestamp=timestamp, data=data, prev_hash=prev.hash, hash=h)
        self.chain.append(block)
        return block

    def verify(self) -> Dict:
        for i in range(1, len(self.chain)):
            cur = self.chain[i]
            prev = self.chain[i-1]
            # rebuild hash
            payload = {"index": cur.index, "timestamp": cur.timestamp, "data": cur.data, "prev_hash": cur.prev_hash}
            expected = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            if cur.prev_hash != prev.hash or cur.hash != expected:
                return {"ok": False, "broken_at": i}
        return {"ok": True, "length": len(self.chain)}

ledger = SimpleLedger()