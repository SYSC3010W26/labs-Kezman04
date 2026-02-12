#!/usr/bin/env python3
"""
SYSC3010 Lab 3 - Firebase (Exercise 2)

- Writes this RPi's SenseHAT temperature, humidity, and pressure to a shared Firebase Realtime DB
  under your username.
- Reads and prints each teammate's 3 most recent values (for each sensor).

Database layout written by this script:

{
  "<username>": {
    "temperature": { "<timestamp>": <float>, ... },
    "humidity":    { "<timestamp>": <float>, ... },
    "pressure":    { "<timestamp>": <float>, ... }
  },
  "<teammate>": { ... }
}

This matches the lab's requirement: each student uses their own username and reads teammates'
most recent values. :contentReference[oaicite:2]{index=2}
"""

import os
import json
import time
from datetime import datetime, timezone

import pyrebase

# SenseHAT is available on the Pi. If you're testing without it, we fall back to dummy values.
try:
    from sense_hat import SenseHat
    _sense = SenseHat()
except Exception:
    _sense = None


CONFIG_ENV = "SYSC3010_LAB3_FIREBASE"


def require_config() -> dict:
    """Load Firebase config from an environment variable (JSON string)."""
    raw = os.environ.get(CONFIG_ENV)
    if not raw:
        raise RuntimeError(
            f"Missing environment variable {CONFIG_ENV}.\n"
            f"Set it like:\n"
            f"export {CONFIG_ENV}='{{\"apiKey\":\"...\",\"authDomain\":\"...\","
            f"\"databaseURL\":\"...\",\"storageBucket\":\"...\"}}'"
        )
    return json.loads(raw)


def utc_timestamp_key() -> str:
    """Firebase key for each sample: ISO UTC string, sortable."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_sensehat_values():
    """Return (temp_c, humidity_pct, pressure_hpa)."""
    if _sense:
        t = float(_sense.get_temperature())
        h = float(_sense.get_humidity())
        p = float(_sense.get_pressure())
        # Round for nicer display/storage
        return round(t, 2), round(h, 2), round(p, 2)

    # Fallback (lets the script run on non-SenseHAT machines)
    return 22.00, 40.00, 1013.00


def write_my_values(db, username: str):
    """Write one sample for each sensor under /<username>/<sensor>/<timestamp>."""
    ts = utc_timestamp_key()
    t, h, p = read_sensehat_values()

    db.child(username).child("temperature").child(ts).set(t)
    db.child(username).child("humidity").child(ts).set(h)
    db.child(username).child("pressure").child(ts).set(p)

    return ts, t, h, p


def last_n_from_sensor(sensor_dict: dict, n: int = 3):
    """
    sensor_dict is like { "<ts>": value, ... }
    Return list of (ts, value) sorted by ts, last n entries.
    """
    if not isinstance(sensor_dict, dict) or not sensor_dict:
        return []
    keys = sorted(sensor_dict.keys())
    last_keys = keys[-n:]
    return [(k, sensor_dict[k]) for k in last_keys]


def print_teammates_latest(root: dict, n: int = 3):
    """Print each user's last n entries for temperature/humidity/pressure."""
    if not isinstance(root, dict) or not root:
        print("Database is empty (no users/data found yet).")
        return

    sensors = ["temperature", "humidity", "pressure"]

    for user, user_node in root.items():
        if not isinstance(user_node, dict):
            continue

        print(f"\n=== {user} ===")
        for s in sensors:
            entries = last_n_from_sensor(user_node.get(s, {}), n=n)
            if not entries:
                print(f"  {s}: (no data)")
                continue

            print(f"  {s} (last {len(entries)}):")
            for ts, val in entries:
                print(f"    {ts} -> {val}")


def main():
    username = input("Enter your username (no spaces): ").strip()
    if not username or " " in username:
        raise RuntimeError("Username must be non-empty and contain no spaces.")

    config = require_config()
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

    print("\nWriting ONE SenseHAT sample to Firebase...")
    ts, t, h, p = write_my_values(db, username)
    print(f"Saved under {username} at {ts}: T={t}C, H={h}%, P={p}hPa")

    # Give Firebase a moment (usually instant, but this avoids rare race conditions)
    time.sleep(0.5)

    print("\nReading teammates' 3 most recent values per sensor...")
    root = db.get().val() or {}
    print_teammates_latest(root, n=3)


if __name__ == "__main__":
    main()

