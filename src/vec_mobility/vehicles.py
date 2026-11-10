"""Synthetic trajectories and validated local trajectory readers."""

import csv
import math
from pathlib import Path
from .config import ROAD_LENGTH
from .uav import uav_positions


def synthetic_frames(duration=40.0):
    frames = []
    for step in range(int(duration * 10)):
        t = step / 10
        vehicles = []
        for i in range(32):
            direction = 1 if i % 2 == 0 else -1
            vx = direction * (22 + i % 12)
            x = (i * 47 + vx * t) % ROAD_LENGTH
            vehicles.append(dict(id=str(i), x_m=x, y_m=9 + (i % 4) * 5.5, vx_mps=vx))
        frames.append(dict(time_s=t, vehicles=vehicles, uavs=uav_positions(t)))
    return frames


def load_frames(path, highd=False, fps=25.0, start=0.0, duration=40.0, x_origin=0.0, y_origin=0.0):
    if fps <= 0 or duration <= 0:
        raise ValueError("fps and duration must be positive")
    groups, seen = {}, set()
    required = {"frame", "id", "x", "y", "xVelocity"} if highd else {"time_s", "id", "x_m", "y_m", "vx_mps"}
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Required columns: {sorted(required)}")
        for row in reader:
            t = (float(row["frame"]) - 1) / fps if highd else float(row["time_s"])
            x = float(row["x"] if highd else row["x_m"]) - x_origin
            y = float(row["y"] if highd else row["y_m"]) - y_origin
            vx = float(row["xVelocity"] if highd else row["vx_mps"])
            if not all(math.isfinite(v) for v in (t, x, y, vx)):
                raise ValueError("Non-finite trajectory value")
            if not start <= t < start + duration:
                continue
            key = (t, row["id"])
            if key in seen:
                raise ValueError(f"Duplicate observation: {key}")
            seen.add(key)
            groups.setdefault(t, []).append(dict(id=row["id"], x_m=x, y_m=y, vx_mps=vx))
    if not groups:
        raise ValueError("No observations in the requested time window")
    origin = min(groups)
    return [dict(time_s=t - origin, vehicles=groups[t], uavs=uav_positions(t - origin)) for t in sorted(groups)]

