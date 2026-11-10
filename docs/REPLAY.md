# Processed Traffic Replay

The processed replay format retains the mixed traffic trajectories used by the scene. Use it to reproduce an existing vehicle scene and add UAVs without replacing the vehicles with newly generated trajectories.

Required columns: `frame,id,x,y,velocity,lane_id,width,height`.

- `frame`: simulation frame index.
- `x,y`: vehicle rectangle origin in metres.
- `velocity`: signed longitudinal velocity.
- `width,height`: the rectangle's longitudinal and lateral dimensions, respectively.
- Time is `frame * dt`. The scene uses `dt=0.1`; the historical filename `highd_processed_1fps.pkl` does not define the time step.

Load a local processed CSV or a trusted local pickle:

```bash
python scripts/preview.py replay --input data/private/highd_processed_1fps.pkl --dt 0.1 --duration 100 --snapshot-time 99.8 --background data/private/01_highway.png --recording-meta data/private/01_recordingMeta.csv --view all --output output/replay
```

The reader preserves positions, velocities, source frame indices and rectangle dimensions. It does not regenerate or interpolate vehicle trajectories. This processed mixed traffic replay differs from the direct official-CSV `highd` reader.

To generate a new mixed replay from locally obtained highD files:

```bash
python scripts/prepare_replay.py --tracks data/private/01_tracks.csv --recording-meta data/private/01_recordingMeta.csv --output data/private/highd_processed_1fps.pkl --seed 48
```

This retains the original scene's downsampling, road expansion, desired-speed sampling, speed update and braking rules. The explicit seed makes new runs repeatable. To recover a particular saved scene exactly, use its saved processed file, rather than regenerating stochastic trajectories.

The optional highway image and recording metadata restore the tiled road background, lane markings, RSU labels and geometric ellipses of the original top view. The ellipses are visual guides, not calculated communication coverage.

Outputs include `top_original.png` (vehicles and RSUs), `top_view.png` and `top_view.gif` (with UAVs), `spatial_view.png` and `spatial_view.gif` (the same vehicles in a spatial view), and `playback.html`. `--snapshot-time` selects the nearest source observation. Source times are preserved.

Processed data and background images must be supplied locally. Data-derived output is subject to the source dataset's terms. The independent synthetic example remains available through the `demo` command.
