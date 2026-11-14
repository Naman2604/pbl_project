"""Thread-safe parking statistics shared between the video thread and the API."""
import threading
import time

_lock = threading.Lock()

_stats = {
    "total_slots": 0,
    "occupied": 0,
    "available": 0,
    "occupancy_rate": 0.0,   # percent, 0-100
    "updated_at": None,      # unix timestamp of the last update
}
_slots = []                  # [{"id": "P1", "occupied": True}, ...]


def update_stats(slot_data):
    """slot_data: list of booleans / 0-1 ints, one per parking slot."""
    global _slots
    total = len(slot_data)
    occupied = sum(1 for s in slot_data if s)
    rate = round(occupied / total * 100, 1) if total else 0.0

    with _lock:
        _stats.update(
            total_slots=total,
            occupied=occupied,
            available=total - occupied,
            occupancy_rate=rate,
            updated_at=time.time(),
        )
        _slots = [{"id": f"P{i}", "occupied": bool(s)} for i, s in enumerate(slot_data, 1)]


def get_stats():
    with _lock:
        data = dict(_stats)
    # Deprecated aliases so older frontend builds that still read the old
    # key names keep working. Prefer total_slots / occupancy_rate.
    data["total"] = data["total_slots"]
    data["occupancy"] = data["occupancy_rate"]
    return data


def get_slots():
    with _lock:
        return list(_slots)
