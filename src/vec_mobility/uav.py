"""Three prescribed flight paths; each UAV has a constant altitude."""

import math
from .config import ROAD_LENGTH, RSU_Y, ALTITUDES


def uav_positions(time_s):
    x_span, y_span, speed = ROAD_LENGTH - 240.0, 42.0, 35.0
    period = max(
        x_span / speed,
        math.hypot(x_span, 0.38 * y_span * 2 * math.pi) / speed,
        math.hypot(x_span, 0.34 * y_span * 2 * math.pi) / speed,
        math.hypot(0.22 * ROAD_LENGTH * 2 * math.pi, 0.26 * y_span * 4 * math.pi) / speed,
        1.0,
    )
    result = []
    for i, z in enumerate(ALTITUDES):
        cycle = time_s / period + i / 3
        phase = cycle % 2
        phase = phase if phase <= 1 else 2 - phase
        if i == 0:
            x = 120 + x_span * phase
            y = RSU_Y + 0.38 * y_span * math.sin(2 * math.pi * phase)
        elif i == 1:
            x = ROAD_LENGTH - 120 - x_span * phase
            y = RSU_Y - 0.34 * y_span * math.cos(2 * math.pi * phase + 0.5)
        else:
            phase = cycle % 1
            x = ROAD_LENGTH / 2 + 0.22 * ROAD_LENGTH * math.sin(2 * math.pi * phase)
            y = RSU_Y + 0.26 * y_span * math.sin(4 * math.pi * phase + 0.8)
        result.append(dict(id=f"U{i + 1}", x_m=x, y_m=y, z_m=z))
    return result

