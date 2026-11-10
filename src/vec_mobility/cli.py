"""Command line interface for local trajectory previews."""

import argparse
import math
from pathlib import Path
from .vehicles import load_frames, synthetic_frames
from .visualization.html import export_view


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    for mode in ("demo", "highd", "csv", "replay"):
        p = sub.add_parser(mode)
        p.add_argument("--output", type=Path, default=Path("output/demo") if mode == "demo" else Path("output/private"))
        p.add_argument("--view", choices=("html", "spatial", "all"), default="html")
        p.add_argument("--duration", type=float, default=100 if mode == "replay" else 40)
        p.add_argument("--animation-frames", type=int, default=80)
        p.add_argument("--snapshot-time", type=float, default=None)
        p.add_argument("--background", type=Path, default=None)
        p.add_argument("--recording-meta", type=Path, default=None)
        if mode != "demo":
            p.add_argument("--tracks" if mode == "highd" else "--input", dest="input", type=Path, required=True)
            p.add_argument("--fps", type=float, default=25)
            p.add_argument("--start", type=float, default=0)
            p.add_argument("--x-origin", type=float, default=0)
            p.add_argument("--y-origin", type=float, default=0)
        if mode == "replay":
            p.add_argument("--dt", type=float, default=.1)
    args = parser.parse_args(argv)
    for name in ("duration", "fps"):
        value = getattr(args, name, 1)
        if not math.isfinite(value) or value <= 0:
            parser.error(f"{name} must be positive and finite")
    if args.animation_frames <= 0:
        parser.error("animation-frames must be positive")
    if args.mode == "demo":
        frames = synthetic_frames(args.duration)
        if not frames:
            parser.error("duration must produce at least one 0.1 s sample")
    elif args.mode == "replay":
        from .replay import load_processed
        frames = load_processed(args.input, args.dt, args.start, args.duration)
    else:
        frames = load_frames(args.input, args.mode == "highd", args.fps, args.start,
                             args.duration, args.x_origin, args.y_origin)
    args.output.mkdir(parents=True, exist_ok=True)
    rsus = None
    if args.mode == 'replay' and args.recording_meta is not None:
        import pandas as pd
        from .rsu import positions
        meta = pd.read_csv(args.recording_meta).iloc[0]
        lanes = [float(v) for field in ('upperLaneMarkings','lowerLaneMarkings')
                 for v in str(meta[field]).split(';')]
        rsus = positions()
        for rsu in rsus:
            rsu['y_m'] = (min(lanes)+max(lanes))/2
    if args.view in ("html", "all"):
        export_view(frames, args.output / "playback.html", synthetic=args.mode == "demo", rsus=rsus)
    if args.view in ("spatial", "all"):
        try:
            from .visualization.spatial import render
        except ModuleNotFoundError as exc:
            raise SystemExit("Install optional plotting dependencies: pip install -r requirements-viz.txt") from exc
        render(frames, args.output, args.animation_frames, background=args.background,
               recording_meta=args.recording_meta, snapshot_time=args.snapshot_time,
               legacy=args.mode == "replay")
    if args.mode != "demo" and args.view != "html":
        print("Local data exports contain trajectory coordinates. Review data terms before sharing.")


if __name__ == "__main__":
    main()
