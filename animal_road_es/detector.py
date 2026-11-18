"""Детектор животных на базе YOLOv8 с fallback-режимом."""
import logging

logger = logging.getLogger(__name__)

# Классы COCO -> наши категории (все животные映ятся на один класс "животное")
COCO_TO_CLASS = {
    "dog": "животное",
    "cat": "животное",
    "horse": "животное",
    "sheep": "животное",
    "cow": "животное",
    "pig": "животное",
    "chicken": "животное",
    "bird": "животное",
}


class AnimalDetector:
    def __init__(self, model_path: str, confidence: float = 0.5):
        self.confidence = confidence
        self.model = None
        self._load_model(model_path)

    def _load_model(self, model_path: str):
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            logger.info("YOLOv8 загружена: %s", model_path)
        except Exception as e:  # noqa: BLE001
            logger.warning("YOLOv8 недоступна (%s). Работаем в демо-режиме.", e)

    def detect(self, frame) -> list:
        """Возвращает список обнаружений с bbox, классом и уверенностью."""
        if self.model is None:
            return self._stub_detections(frame)

        results = self.model(frame, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = r.names.get(cls_id, "")
                our_class = COCO_TO_CLASS.get(cls_name)
                if our_class is None:
                    continue
                conf = float(box.conf[0])
                if conf < self.confidence:
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    "class": our_class,
                    "confidence": conf,
                    "bbox": (x1, y1, x2, y2),
                })
        return detections

    def _stub_detections(self, frame) -> list:
        """Демо-режим: возвращает пустой список, чтобы система работала."""
        return []
