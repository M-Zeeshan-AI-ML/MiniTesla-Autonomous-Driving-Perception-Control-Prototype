import csv
from pathlib import Path

FIELDS = [
    "frame", "time_sec", "lane_offset_px", "steering",
    "brake", "num_detections", "processing_ms"
]

class TelemetryLogger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.f = open(self.path, "w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.f, fieldnames=FIELDS)
        self.writer.writeheader()

    def log(self, row):
        self.writer.writerow(row)
        self.f.flush()

    def close(self):
        self.f.close()
