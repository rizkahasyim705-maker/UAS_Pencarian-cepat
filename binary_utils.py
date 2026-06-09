"""
binary_utils.py
Binary Search implementation dengan pencatatan langkah.
"""
from typing import Any


# ── Binary Search Standar ─────────────────────────────────────
def binary_search(arr: list[str], target: str) -> int:
    """
    Mencari target dalam list terurut arr.
    Mengembalikan index jika ditemukan, -1 jika tidak.
    Perbandingan case-insensitive.
    """
    lo, hi = 0, len(arr) - 1
    target_lower = target.lower()

    while lo <= hi:
        mid = (lo + hi) // 2
        mid_val = arr[mid].lower()

        if mid_val == target_lower:
            return mid
        elif mid_val < target_lower:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1


# ── Binary Search dengan Langkah ──────────────────────────────
def binary_search_steps(arr: list[str], target: str) -> list[dict]:
    """
    Mengembalikan list langkah pencarian Binary Search.
    Setiap langkah berisi: step, lo, hi, mid, value, found, go.
    """
    lo, hi = 0, len(arr) - 1
    target_lower = target.lower()
    steps = []
    step_num = 1

    while lo <= hi:
        mid = (lo + hi) // 2
        mid_val = arr[mid]

        if mid_val.lower() == target_lower:
            steps.append({
                "step": step_num,
                "lo": lo, "hi": hi, "mid": mid,
                "value": mid_val,
                "found": True,
                "go": "found",
            })
            break
        elif mid_val.lower() < target_lower:
            steps.append({
                "step": step_num,
                "lo": lo, "hi": hi, "mid": mid,
                "value": mid_val,
                "found": False,
                "go": "right",
            })
            lo = mid + 1
        else:
            steps.append({
                "step": step_num,
                "lo": lo, "hi": hi, "mid": mid,
                "value": mid_val,
                "found": False,
                "go": "left",
            })
            hi = mid - 1

        step_num += 1

    return steps


# ── Binary Search pada list of dict ──────────────────────────
def binary_search_dict(
    arr: list[dict],
    target: str,
    key: str = "name",
) -> dict | None:
    """
    Binary search pada list of dict yang sudah diurutkan berdasarkan `key`.
    """
    names = [item[key] for item in arr]
    idx = binary_search(names, target)
    return arr[idx] if idx != -1 else None
