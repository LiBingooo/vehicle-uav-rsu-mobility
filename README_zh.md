# 车辆–UAV–RSU 轨迹场景工具

本项目基于 [highD（Highway Drone Dataset）真实高速公路车辆轨迹数据集](https://levelxdata.com/highd-dataset/)，构建车辆、无人机（UAV）与路侧单元（RSU）联合移动场景，支持轨迹读取、场景回放、俯视图和三维空间动画。

车辆场景使用基于 highD 构建的混合交通回放；UAV 路径与 RSU 部署由场景模型生成。已有场景可直接读取保存的处理后轨迹，保留车辆原有运动状态。使用 highD 时，需先向数据集提供方申请访问权限。

## highD 数据获取

highD 是通过无人机航拍采集的德国高速公路车辆轨迹数据集。

1. 打开 [highD 官方网站](https://levelxdata.com/highd-dataset/)。
2. 找到 **Application for Access for Non-Commercial Use** 申请表。
3. 填写姓名、机构信息、官方邮箱及研究用途，阅读并同意使用条款后提交。
4. 等待官方人工审核，通过后按提供方指引获取数据。
5. 将所需记录文件放入 `data/private/`。保留 `01_tracks.csv` 和 `01_recordingMeta.csv` 等文件，并从记录元数据读取帧率。

本仓库不提供 highD 数据下载镜像。数据使用与分享须遵守其官方条款，详细接入方法见 [highD 使用说明](docs/HIGHD.md)。

## 场景回放

安装可视化依赖后，加载已有处理后轨迹及其道路背景：

```powershell
pip install -r requirements-viz.txt
python scripts/preview.py replay --input data/private/highd_processed_1fps.pkl --background data/private/01_highway.png --recording-meta data/private/01_recordingMeta.csv --snapshot-time 99.8 --view all --output output/replay
```

该入口保留车辆位置、速度、尺寸和帧时间。输出包括不加 UAV 的原版俯视图、叠加 UAV 的俯视图、同一场景的三维空间图及动画。详见 [处理后轨迹回放](docs/REPLAY.md)。

从原始 highD 文件生成混合交通回放：

```powershell
python scripts/prepare_replay.py --tracks data/private/01_tracks.csv --recording-meta data/private/01_recordingMeta.csv --output data/private/highd_processed_1fps.pkl --seed 48
```

预处理包括道路扩展和虚拟车辆运动模型。重新预处理会生成一份带随机种子的混合轨迹；精确重放已有场景时应使用其保存的轨迹文件。

## 合成示例

需要 Python 3.10 或更高版本。网页回放无需安装第三方依赖：

```powershell
python scripts/preview.py demo --view html --output output/demo
```

在浏览器中打开 `output/demo/playback.html`。生成俯视图、三维空间图和 GIF：

```powershell
pip install -r requirements-viz.txt
python scripts/preview.py demo --view all --output output/demo
```

此入口为独立的合成车辆示例，预生成结果位于 [assets/demo/](assets/demo/)。

## 加载真实轨迹

以记录帧率为 25 fps 的文件为例：

```powershell
python scripts/preview.py highd --tracks data/private/01_tracks.csv --fps 25 --view all --output output/private
```

也可加载自有 CSV，字段为 `time_s,id,x_m,y_m,vx_mps`：

```powershell
python scripts/preview.py csv --input data/private/scene.csv --view all --output output/private
```

## 功能

- highD 及通用 CSV 车辆轨迹读取。
- 处理后混合轨迹的读取、预处理和原版场景回放。
- UAV 预设移动路径和 RSU 空间部署。
- HTML 交互回放、俯视图、三维空间图及 GIF 导出。

模块结构见 [工程架构](docs/ARCHITECTURE.md)，数据来源见 [数据来源说明](docs/PROVENANCE.md)。

## 可用性

相关论文目前正在审阅中，完整实现暂不公开。本仓库提供轨迹与场景可视化部分。
