# Data Sources and Scene Components

| Component | Source |
| --- | --- |
| Real vehicle trajectories | [highD (Highway Drone Dataset)](https://levelxdata.com/highd-dataset/) |
| Mixed traffic replay | highD-based road expansion and virtual vehicle dynamics, implemented in `preprocess.py`; saved observations read unchanged by `replay.py` |
| UAV trajectories | Prescribed mathematical flight paths implemented in `src/vec_mobility/uav.py` |
| RSU deployment | Geometric scene model implemented in `src/vec_mobility/rsu.py` |
| Bundled vehicle examples | Deterministic synthetic generator in `src/vec_mobility/vehicles.py` |
| Road surface in bundled visualizations | Generated schematic road |

highD provides the real vehicle trajectories. UAV flight paths and RSU positions are modeled separately; they are not observations from highD. The dataset's recording drone is separate from the scene's simulated UAVs.

The mixed traffic replay includes both recorded and modeled vehicles. Direct official-CSV playback and processed mixed replay are distinct input modes. Preprocessing uses the scene's original update rules and an explicit seed; exact historical vehicle paths require the saved processed file.

The bundled HTML, PNG and GIF examples use synthetic vehicle trajectories. Real highD data must be obtained directly from the provider; see [access instructions](HIGHD.md).
