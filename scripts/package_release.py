"""Build a local upload archive from the explicit source and synthetic-asset inventory."""

import hashlib
import json
from pathlib import Path
import zipfile

FILES = [
    ".gitignore",
    "README.md",
    "README_zh.md",
    "assets/demo/playback.html",
    "assets/demo/spatial_view.gif",
    "assets/demo/spatial_view.png",
    "assets/demo/top_view.png",
    "data/README.md",
    "docs/ARCHITECTURE.md",
    "docs/DATA_POLICY.md",
    "docs/HIGHD.md",
    "docs/AVAILABILITY.md",
    "docs/PROVENANCE.md",
    "docs/REPLAY.md",
    "pyproject.toml",
    "requirements-viz.txt",
    "scripts/package_release.py",
    "scripts/preview.py",
    "scripts/prepare_replay.py",
    "src/vec_mobility/__init__.py",
    "src/vec_mobility/__main__.py",
    "src/vec_mobility/cli.py",
    "src/vec_mobility/config.py",
    "src/vec_mobility/rsu.py",
    "src/vec_mobility/replay.py",
    "src/vec_mobility/preprocess.py",
    "src/vec_mobility/uav.py",
    "src/vec_mobility/vehicles.py",
    "src/vec_mobility/visualization/__init__.py",
    "src/vec_mobility/visualization/html.py",
    "src/vec_mobility/visualization/spatial.py",
    "tests/test_mobility.py"
]


def main():
    root = Path(__file__).resolve().parents[1]
    manifest = []
    for name in FILES:
        path = root / name
        if path.is_symlink() or root not in path.resolve().parents:
            raise ValueError(f"Unexpected path: {name}")
        data = path.read_bytes()
        manifest.append(dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    html = (root / "assets/demo/playback.html").read_text(encoding="utf-8")
    payload = json.loads(html.split('type="application/json">',1)[1].split("</script>",1)[0])
    if payload.get("synthetic") is not True:
        raise ValueError("Only the synthetic example may be bundled")
    record = root / "RELEASE_MANIFEST.json"
    record.write_text(json.dumps(dict(status="paper under review; trajectory and visualization components only", files=manifest),indent=2)+"\n",encoding="utf-8")
    archive = root.parent / "VEC_MOBILITY_RELEASE_UPLOAD.zip"
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as bundle:
        for name in [*FILES, "RELEASE_MANIFEST.json"]:
            bundle.write(root/name, arcname=f"{root.name}/{name}")
    print(f"Built {archive}: {len(FILES)+1} files, {archive.stat().st_size} bytes")


if __name__ == "__main__":
    main()
