"""Глобальная конфигурация проекта."""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(RESOURCES_DIR, "config.json")
RULES_FILE = os.path.join(RESOURCES_DIR, "rules.json")
ONTOLOGY_FILE = os.path.join(RESOURCES_DIR, "animal_road_ontology.owl")
LOG_FILE = os.path.join(LOGS_DIR, "events.csv")

MODEL_PATH = os.path.join(MODELS_DIR, "yolov8n.pt")

# Значения по умолчанию (переопределяются из resources/config.json)
DEFAULTS = {
    "camera_index": 0,
    "video_source": "",              # если задано — используется вместо камеры
    "confidence_threshold": 0.5,
    "frame_width": 960,
    "frame_height": 540,
    "show_zone_overlay": True,
    "log_enabled": True,
    "road_zone": [0.15, 0.55, 0.85, 1.00],       # [x1, y1, x2, y2] норм.
    "shoulder_left_zone": [0.00, 0.50, 0.15, 1.00],
    "shoulder_right_zone": [0.85, 0.50, 1.00, 1.00],
    "risk_colors": {"low": "green", "medium": "yellow", "high": "red"},
}


def load_config() -> dict:
    """Загружает config.json и дополняет значениями по умолчанию."""
    cfg = dict(DEFAULTS)
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    return cfg
