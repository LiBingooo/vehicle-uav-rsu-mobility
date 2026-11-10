"""Read the processed mixed-traffic trajectory format used by the scene."""

import math
from pathlib import Path

from .uav import uav_positions


def load_processed(path, dt=.1, start=0.0, duration=100.0):
    """Preserve source frames, times, positions, velocities and vehicle dimensions.

    Pickles must come from a trusted local source. CSV uses the same column schema.
    """
    import pandas as pd

    if not all(math.isfinite(v) for v in (dt, start, duration)) or dt <= 0 or duration <= 0:
        raise ValueError("dt and duration must be positive and all time values finite")
    path = Path(path)
    if path.suffix.lower() in {'.pkl', '.pickle'}:
        data = pd.read_pickle(path)
    elif path.suffix.lower() == '.csv':
        data = pd.read_csv(path)
    else:
        raise ValueError("Processed replay must be a trusted pickle or CSV")
    required = {'frame', 'id', 'x', 'y', 'velocity', 'lane_id', 'width', 'height'}
    if not required.issubset(data.columns):
        raise ValueError(f"Required processed columns: {sorted(required)}")
    data = data[(data.frame * dt >= start) & (data.frame * dt < start + duration)]
    frames = []
    for number, group in data.groupby('frame', sort=True):
        vehicles = []
        for row in group.itertuples(index=False):
            values = (row.x, row.y, row.velocity, row.width, row.height)
            if not all(math.isfinite(float(v)) for v in values) or row.width <= 0 or row.height <= 0:
                raise ValueError("Invalid vehicle coordinates or dimensions")
            vehicles.append(dict(id=str(row.id), x_m=float(row.x), y_m=float(row.y),
                                 vx_mps=float(row.velocity), length_m=float(row.width),
                                 width_m=float(row.height), lane_id=int(row.lane_id)))
        time_s = int(number) * dt
        frames.append(dict(source_frame=int(number), time_s=time_s,
                           vehicles=vehicles, uavs=uav_positions(time_s)))
    if not frames:
        raise ValueError("No processed observations in the requested time window")
    return frames
