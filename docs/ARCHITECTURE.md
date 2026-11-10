# 工程架构

```text
VEC_MOBILITY_RELEASE/
  README.md / README_zh.md       项目说明与运行方法
  pyproject.toml                Python 包与命令行配置
  requirements-viz.txt          可视化依赖
  src/vec_mobility/
    config.py                   场景几何参数
    vehicles.py                 合成车辆、通用 CSV、highD 读取
    replay.py                   保存的混合轨迹读取
    preprocess.py               highD 混合交通预处理
    uav.py                      UAV 预设移动路径
    rsu.py                      RSU 位置与几何分段
    cli.py / __main__.py        命令行入口
    visualization/
      html.py                   俯视与侧视 HTML 回放
      spatial.py                俯视图、三维空间图、GIF
  scripts/
    preview.py                  演示入口
    prepare_replay.py           混合轨迹生成入口
    package_release.py          文件清单与归档生成
  assets/demo/                  合成场景示例
  data/README.md                本地数据使用说明
  docs/                         数据来源、使用说明与架构
  tests/                        输入与导出验证
  RELEASE_MANIFEST.json         文件清单及校验值
```

## 数据流程

保存的处理后轨迹 / highD 官方 CSV / 合成车辆 → 时间帧 → UAV 路径与 RSU 部署 → HTML / PNG / GIF。

原版场景由处理后轨迹驱动；`replay` 模式保留车辆坐标、速度、尺寸和时间，并支持原版道路背景。`demo` 模式提供独立的合成示例。

HTML 回放只依赖 Python 标准库；空间绘图使用 numpy、pandas、matplotlib 和 Pillow。

## 模块接口

- `vehicles.load_frames(...)`：读取并校验轨迹，输出按时间排序的场景帧。
- `vehicles.synthetic_frames(...)`：生成可直接运行的合成示例。
- `uav.uav_positions(time_s)`：返回指定时刻的 UAV 位置。
- `rsu.positions()`：返回 RSU 部署坐标。
- `rsu.associate(x)`：根据道路几何分段确定 RSU 归属。
- `visualization.html.export_view(...)`：导出自包含网页回放。
- `visualization.spatial.render(...)`：导出图片和动画。

场景帧包含 `time_s`、`vehicles` 和 `uavs`。车辆位置与速度采用 SI 单位。UAV 按固定高度的预设路径移动；空间图采用不同轴向显示比例以便观察。

真实车辆轨迹来自 [highD](https://levelxdata.com/highd-dataset/)，访问方式见 [highD 使用说明](HIGHD.md)。
