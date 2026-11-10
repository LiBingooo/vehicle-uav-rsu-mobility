# Vehicle-UAV-RSU Mobility Scenes

A vehicle-UAV-RSU scene toolkit built around real highway vehicle trajectories from the [highD (Highway Drone Dataset)](https://levelxdata.com/highd-dataset/). It supports trajectory loading, browser playback, top views, and spatial animations.

The vehicle scene uses a highD-based mixed traffic replay. UAV paths and RSU deployment are modeled separately. The processed replay reader preserves an existing scene's vehicle motion. To use highD data, obtain access from the provider first.

## Get the highD Dataset

1. Visit the [official highD website](https://levelxdata.com/highd-dataset/).
2. Locate **Application for Access for Non-Commercial Use**.
3. Enter your name, institution, official email address, and intended research use; review and accept the terms.
4. Submit the request for manual review and follow the provider's access instructions after approval.
5. Place the required recording files under `data/private/` and read the frame rate from the recordingMeta CSV.

This repository does not host a dataset mirror. See [highD usage](docs/HIGHD.md) for input files and commands.

## Replay the Traffic Scene

Install the plotting dependencies and load the locally saved replay with its road background:

```bash
pip install -r requirements-viz.txt
python scripts/preview.py replay --input data/private/highd_processed_1fps.pkl --background data/private/01_highway.png --recording-meta data/private/01_recordingMeta.csv --snapshot-time 99.8 --view all --output output/replay
```

This preserves source vehicle positions, velocities, dimensions and times. Outputs include the vehicle/RSU top view, the same view with UAVs, and a spatial view and animation of the same scene. See [processed replay](docs/REPLAY.md).

To build a mixed replay from locally obtained raw highD files:

```bash
python scripts/prepare_replay.py --tracks data/private/01_tracks.csv --recording-meta data/private/01_recordingMeta.csv --output data/private/highd_processed_1fps.pkl --seed 48
```

Preprocessing combines road expansion with virtual vehicle motion. A new preprocessing run generates a seeded mixed replay; use the saved replay file for exact playback of an existing scene.

## Synthetic Example

Python 3.10+. Browser playback requires only the standard library:

```bash
python scripts/preview.py demo --view html --output output/demo
```

Open `output/demo/playback.html`. For top/spatial PNGs and GIF animation:

```bash
pip install -r requirements-viz.txt
python scripts/preview.py demo --view all --output output/demo
```

Outputs: `playback.html`, `top_view.png`, `spatial_view.png`, and `spatial_view.gif`. Pre-generated synthetic examples are in [assets/demo/](assets/demo/).

Optional package installation: `pip install -e ".[viz]"`, followed by `vec-mobility demo --view all`.

## Load Trajectories

For a highD recording with a frame rate of 25 fps:

```bash
python scripts/preview.py highd --tracks data/private/01_tracks.csv --fps 25 --view all --output output/private
```

For your own CSV with fields `time_s,id,x_m,y_m,vx_mps`:

```bash
python scripts/preview.py csv --input data/private/scene.csv --view all --output output/private
```

## Features

- Vehicle trajectory readers for highD and generic CSV.
- Processed mixed traffic replay, preprocessing and original-scene rendering.
- Prescribed UAV paths and spatial RSU deployment.
- HTML playback and top/spatial PNG and GIF exports.

See [architecture](docs/ARCHITECTURE.md), [data sources](docs/PROVENANCE.md), [data policy](docs/DATA_POLICY.md), and the [Chinese guide](README_zh.md).

## Availability

The associated paper is currently under review. The complete implementation is not publicly available at this time. This repository provides the trajectory and scene visualization components.
