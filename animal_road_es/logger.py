"""CSV-лог событий."""
import csv
import os
from datetime import datetime


class EventLogger:
    HEADERS = ["timestamp", "class", "confidence", "position", "risk",
               "color", "rule_id"]

    def __init__(self, path: str, enabled: bool = True):
        self.path = path
        self.enabled = enabled
        if self.enabled and not os.path.exists(path):
            with open(path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(self.HEADERS)

    def log(self, detections: list, assessment: dict):
        if not self.enabled:
            return
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not detections:
                writer.writerow([ts, "-", "-", "none",
                                 assessment["risk"], assessment["color"],
                                 assessment["rule_id"]])
                return
            for det in detections:
                writer.writerow([
                    ts, det["class"], f"{det['confidence']:.3f}",
                    det.get("position", "none"),
                    assessment["risk"], assessment["color"],
                    assessment["rule_id"],
                ])
