"""Small portability and trajectory integrity checks; no external data is used."""

import csv
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vec_mobility.rsu import associate, positions
from vec_mobility.uav import uav_positions
from vec_mobility.vehicles import load_frames, synthetic_frames
from vec_mobility.visualization.html import export_view


class MobilityTests(unittest.TestCase):
    def write_csv(self, directory, fields, rows):
        path = Path(directory) / "fixture.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_rsu_geometry(self):
        rsus = positions()
        self.assertEqual(len(rsus), 6)
        for i, rsu in enumerate(rsus):
            self.assertEqual(associate(rsu["x_m"]), i)
        self.assertEqual(associate(-1), 0)
        self.assertEqual(associate(1600), 5)

    def test_paths_keep_fixed_altitude_and_speed_bound(self):
        for time in (0, .1, 10, 39.9, 100):
            current, later = uav_positions(time), uav_positions(time + .001)
            self.assertEqual([u["z_m"] for u in current], [75., 92., 108.])
            for a, b in zip(current, later):
                self.assertLessEqual(math.dist([a["x_m"], a["y_m"]], [b["x_m"], b["y_m"]]) / .001, 35.001)

    def test_highd_time_and_origin(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_csv(tmp, ["frame","id","x","y","xVelocity"], [
                dict(frame=26,id=1,x=120,y=10,xVelocity=22),
                dict(frame=51,id=1,x=142,y=10,xVelocity=22)])
            frames = load_frames(path, highd=True, fps=25, start=1, duration=2, x_origin=100)
            self.assertEqual([f["time_s"] for f in frames], [0, 1])
            self.assertEqual(frames[0]["vehicles"][0]["x_m"], 20)

    def test_duplicate_and_missing_fields_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = dict(time_s=0,id=1,x_m=10,y_m=9,vx_mps=20)
            path = self.write_csv(tmp, list(row), [row, row])
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                load_frames(path)
            path = self.write_csv(tmp, ["id"], [dict(id=1)])
            with self.assertRaisesRegex(ValueError, "Required"):
                load_frames(path)

    def test_processed_replay_preserves_source_values(self):
        from vec_mobility.replay import load_processed
        with tempfile.TemporaryDirectory() as tmp:
            row = dict(frame=998,id=47,x=1543.375,y=22.33,velocity=31.3,lane_id=5,width=4.75,height=1.92)
            path = self.write_csv(tmp,list(row),[row])
            frame = load_processed(path,start=99,duration=1)[0]
            self.assertEqual(frame['source_frame'],998)
            self.assertAlmostEqual(frame['time_s'],99.8)
            car = frame['vehicles'][0]
            self.assertEqual((car['x_m'],car['y_m'],car['vx_mps']),(1543.375,22.33,31.3))
            self.assertEqual((car['length_m'],car['width_m']),(4.75,1.92))

    def test_html_payload_and_safe_identifier(self):
        frames = synthetic_frames(.2)
        frames[0]["vehicles"][0]["id"] = "</script><script>bad()</script>"
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "demo.html"
            export_view(frames, output, synthetic=True)
            html = output.read_text(encoding="utf-8")
            payload = html.split('type="application/json">', 1)[1].split("</script>", 1)[0]
            data = json.loads(payload)
            self.assertTrue(data["synthetic"])
            self.assertEqual(len(data["frames"]), 2)
            self.assertNotIn("</script>", payload)


if __name__ == "__main__":
    unittest.main()
