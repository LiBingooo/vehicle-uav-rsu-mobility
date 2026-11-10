"""Mixed traffic expansion rules for locally obtained highD recordings."""

from pathlib import Path
import numpy as np
import pandas as pd

SOURCE_FPS = 25
TARGET_FPS = 10
DT = 1.0 / TARGET_FPS


def build_processed(tracks, recording_meta, output, seed=48):
    rng = np.random.RandomState(seed)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        df_tracks = pd.read_csv(tracks)
        df_rec = pd.read_csv(recording_meta)
    except FileNotFoundError as e:
        raise
    TILE_LENGTH = 400.0
    TOTAL_LENGTH = 1600.0
    right_zone_start = TOTAL_LENGTH - TILE_LENGTH
    try:
        upper_lanes = [float(x) for x in df_rec['upperLaneMarkings'][0].split(';')]
        lower_lanes = [float(x) for x in df_rec['lowerLaneMarkings'][0].split(';')]
        all_lanes = sorted(list(set(upper_lanes + lower_lanes)))
    except:
        all_lanes = [0, 10, 20]
        upper_lanes, lower_lanes = ([], [])
    step_size = max(1, int(SOURCE_FPS / TARGET_FPS))
    df_tracks = df_tracks[df_tracks['frame'] % step_size == 0].copy()
    min_frame = df_tracks['frame'].min()
    df_tracks['sim_step'] = ((df_tracks['frame'] - min_frame) / step_size).astype(int)
    df_base = df_tracks[['sim_step', 'id', 'x', 'y', 'xVelocity', 'laneId', 'width', 'height']].rename(columns={'sim_step': 'frame', 'xVelocity': 'velocity', 'laneId': 'lane_id'})
    df_base = df_base[df_base['x'] < TILE_LENGTH]
    lane_stats = {}
    for lid in df_base['lane_id'].unique():
        v_data = df_base[df_base['lane_id'] == lid]['velocity']
        std_val = v_data.std()
        if np.isnan(std_val) or std_val < 3.0:
            std_val = 5.0
        lane_stats[lid] = {'mean': v_data.mean(), 'std': std_val}
    final_frames = []
    virtual_vehicles = {}
    VIRTUAL_ID_OFFSET = 1000000
    MAX_SIM_FRAMES = df_base['frame'].max()

    def get_desired_speed(lane_id, current_v):
        stats = lane_stats.get(lane_id, {'mean': 30.0, 'std': 5.0})
        desired = rng.normal(stats['mean'], stats['std'])
        if current_v > 0:
            return max(15.0, desired)
        else:
            return min(-15.0, desired)
    num_tiles = int(np.ceil(TOTAL_LENGTH / TILE_LENGTH))
    TIME_SHIFT = 150
    for tile_i in range(num_tiles):
        shifted_frame_idx = (0 + tile_i * TIME_SHIFT) % MAX_SIM_FRAMES
        snapshot = df_base[df_base['frame'] == shifted_frame_idx]
        tile_start_x = tile_i * TILE_LENGTH
        for _, row in snapshot.iterrows():
            new_x = row['x'] + tile_start_x
            vid = int(row['id'] + tile_i * VIRTUAL_ID_OFFSET)
            should_spawn = False
            if row['velocity'] > 0:
                if new_x >= TILE_LENGTH:
                    should_spawn = True
            elif new_x < right_zone_start:
                should_spawn = True
            if should_spawn and new_x < TOTAL_LENGTH:
                target_v = get_desired_speed(row['lane_id'], row['velocity'])
                virtual_vehicles[vid] = {'x': new_x, 'y': row['y'], 'v': row['velocity'], 'lane': row['lane_id'], 'w': row['width'], 'h': row['height'], 'target_v': target_v}
    for f in range(MAX_SIM_FRAMES):
        current_frame_data = []
        real_data = df_base[df_base['frame'] == f]
        real_blue_ids = set()
        real_red_ids = set()
        lane_positions = {}
        for _, row in real_data.iterrows():
            if row['velocity'] > 0:
                real_blue_ids.add(row['id'])
                current_frame_data.append(row.to_dict())
                lid = row['lane_id']
                if lid not in lane_positions:
                    lane_positions[lid] = []
                lane_positions[lid].append((row['x'], row['velocity'], row['id']))
                if row['x'] > TILE_LENGTH - 20.0:
                    target_v = get_desired_speed(row['lane_id'], row['velocity'])
                    virtual_vehicles[row['id']] = {'x': row['x'], 'y': row['y'], 'v': row['velocity'], 'lane': row['lane_id'], 'w': row['width'], 'h': row['height'], 'target_v': target_v}
            else:
                mapped_x = right_zone_start + row['x']
                mapped_id = int(row['id'] + VIRTUAL_ID_OFFSET * 9)
                real_red_ids.add(mapped_id)
                car_dict = row.to_dict()
                car_dict['id'] = mapped_id
                car_dict['x'] = mapped_x
                current_frame_data.append(car_dict)
                lid = row['lane_id']
                if lid not in lane_positions:
                    lane_positions[lid] = []
                lane_positions[lid].append((mapped_x, row['velocity'], mapped_id))
                if mapped_x < right_zone_start + 20.0:
                    target_v = get_desired_speed(row['lane_id'], row['velocity'])
                    virtual_vehicles[mapped_id] = {'x': mapped_x, 'y': row['y'], 'v': row['velocity'], 'lane': row['lane_id'], 'w': row['width'], 'h': row['height'], 'target_v': target_v}
        for vid, car in virtual_vehicles.items():
            if vid in real_blue_ids or vid in real_red_ids:
                continue
            lid = car['lane']
            if lid not in lane_positions:
                lane_positions[lid] = []
            lane_positions[lid].append((car['x'], car['v'], vid))
        for lid in lane_positions:
            lane_positions[lid].sort(key=lambda item: item[0])
        dead_vehicles = []
        for vid, car in virtual_vehicles.items():
            if vid in real_blue_ids:
                continue
            if vid in real_red_ids:
                continue
            target = car['target_v']
            theta, sigma = (0.8, 2.0)
            noise = rng.randn()
            delta_v = theta * (target - car['v']) * DT + sigma * noise * np.sqrt(DT)
            lid = car['lane']
            vehicles_in_lane = lane_positions.get(lid, [])
            my_idx = -1
            for i, v_info in enumerate(vehicles_in_lane):
                if v_info[2] == vid:
                    my_idx = i
                    break
            if my_idx != -1:
                if car['v'] > 0:
                    if my_idx + 1 < len(vehicles_in_lane):
                        front_x, front_v, _ = vehicles_in_lane[my_idx + 1]
                        dist = front_x - car['x']
                        if 0 < dist < 30.0 and car['v'] > front_v:
                            delta_v = -4.0 * DT
                elif my_idx - 1 >= 0:
                    front_x, front_v, _ = vehicles_in_lane[my_idx - 1]
                    dist = car['x'] - front_x
                    if 0 < dist < 30.0 and car['v'] < front_v:
                        delta_v = 4.0 * DT
            car['v'] += delta_v
            if target > 0:
                car['v'] = np.clip(car['v'], 5.0, 55.0)
            else:
                car['v'] = np.clip(car['v'], -55.0, -5.0)
            car['x'] += car['v'] * DT
            current_frame_data.append({'frame': f, 'id': vid, 'x': car['x'], 'y': car['y'], 'velocity': car['v'], 'lane_id': car['lane'], 'width': car['w'], 'height': car['h']})
            if car['v'] > 0 and car['x'] > TOTAL_LENGTH:
                dead_vehicles.append(vid)
            if car['v'] < 0 and car['x'] < 0:
                dead_vehicles.append(vid)
        for vid in dead_vehicles:
            del virtual_vehicles[vid]
        final_frames.extend(current_frame_data)
    df_final = pd.DataFrame(final_frames)
    df_final = df_final.sort_values(by=['frame', 'id'])
    cols = ['frame', 'id', 'x', 'y', 'velocity', 'lane_id', 'width', 'height']
    df_final = df_final[cols]
    df_final = df_final.astype({'frame': 'int32', 'id': 'int32', 'lane_id': 'int32', 'x': 'float32', 'y': 'float32', 'velocity': 'float32', 'width': 'float32', 'height': 'float32'})
    try:
        df_final.to_pickle(output)
    except Exception as e:
        raise
    return df_final
