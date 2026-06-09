"""
hash_utils.py
Hash Table implementation menggunakan Separate Chaining.
"""


class HashTable:
    def __init__(self, size: int = 101):
        self.size = size
        self.table: list[list] = [[] for _ in range(size)]

    # ── Hash Function (Polynomial Rolling) ───────────────────
    def _hash(self, key: str) -> int:
        """Menghitung hash value dari string key."""
        h = 0
        prime = 31
        for ch in key.lower():
            h = (h * prime + ord(ch)) % self.size
        return h

    # ── Insert ────────────────────────────────────────────────
    def insert(self, key: str, value: dict) -> None:
        idx = self._hash(key)
        # update jika key sudah ada
        for i, (k, _) in enumerate(self.table[idx]):
            if k.lower() == key.lower():
                self.table[idx][i] = (key, value)
                return
        self.table[idx].append((key, value))

    # ── Search ────────────────────────────────────────────────
    def search(self, key: str) -> dict | None:
        idx = self._hash(key)
        for k, v in self.table[idx]:
            if k.lower() == key.lower():
                return v
        return None

    # ── Search dengan detail langkah ──────────────────────────
    def search_steps(self, key: str) -> tuple[dict, list]:
        idx = self._hash(key)
        steps = {
            "hash_value": sum(ord(c) for c in key.lower()),   # nilai mentah
            "bucket_index": idx,
        }
        chain = [{"name": k, "data": v} for k, v in self.table[idx]]
        return steps, chain

    # ── Delete ────────────────────────────────────────────────
    def delete(self, key: str) -> bool:
        idx = self._hash(key)
        for i, (k, _) in enumerate(self.table[idx]):
            if k.lower() == key.lower():
                self.table[idx].pop(i)
                return True
        return False

    # ── Info ──────────────────────────────────────────────────
    def load_factor(self) -> float:
        total = sum(len(bucket) for bucket in self.table)
        return total / self.size

    def stats(self) -> dict:
        lengths = [len(b) for b in self.table]
        filled  = sum(1 for l in lengths if l > 0)
        return {
            "size": self.size,
            "filled_buckets": filled,
            "max_chain": max(lengths),
            "load_factor": round(self.load_factor(), 3),
        }
