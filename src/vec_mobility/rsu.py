"""Spatial RSU deployment and segment membership."""

from .config import NUM_RSUS, ROAD_LENGTH, RSU_Y, RSU_Z


def associate(x):
    return max(0, min(NUM_RSUS - 1, int(x // (ROAD_LENGTH / NUM_RSUS))))


def positions():
    return [dict(id=f"R{i}", x_m=(i + .5) * ROAD_LENGTH / NUM_RSUS,
                 y_m=RSU_Y, z_m=RSU_Z) for i in range(NUM_RSUS)]

