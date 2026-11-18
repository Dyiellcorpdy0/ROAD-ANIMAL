"""Определение положения животного: дорога / обочина / вне зоны."""
import logging

logger = logging.getLogger(__name__)


class PositionInterpreter:
    def __init__(self, config: dict):
        self.road_zone = config["road_zone"]
        self.shoulder_left = config["shoulder_left_zone"]
        self.shoulder_right = config["shoulder_right_zone"]

    def interpret(self, detections: list, frame_size: tuple) -> list:
        """Дополняет каждое обнаружение полем position."""
        width, height = frame_size
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            cx = ((x1 + x2) / 2) / width
            cy = ((y1 + y2) / 2) / height

            if self._in_zone(cx, cy, self.road_zone):
                det["position"] = "road"
            elif self._in_zone(cx, cy, self.shoulder_left) or \
                    self._in_zone(cx, cy, self.shoulder_right):
                det["position"] = "shoulder"
            else:
                det["position"] = "none"
        return detections

    @staticmethod
    def _in_zone(cx: float, cy: float, zone: list) -> bool:
        x1, y1, x2, y2 = zone
        return x1 <= cx <= x2 and y1 <= cy <= y2
