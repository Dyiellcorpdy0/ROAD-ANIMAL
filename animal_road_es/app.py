"""Точка входа. Запуск: python app.py"""
import logging
import tkinter as tk

from config import load_config, RULES_FILE, ONTOLOGY_FILE, LOG_FILE, MODEL_PATH
from knowledge_base import KnowledgeBase
from inference_engine import InferenceEngine
from detector import AnimalDetector
from logger import EventLogger
from test_console import TestConsoleApp


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    cfg = load_config()

    kb = KnowledgeBase(ONTOLOGY_FILE, RULES_FILE)
    engine = InferenceEngine(kb)
    detector = AnimalDetector(MODEL_PATH, cfg["confidence_threshold"])
    event_logger = EventLogger(LOG_FILE, enabled=cfg.get("log_enabled", True))

    root = tk.Tk()
    TestConsoleApp(root, cfg, detector, engine, event_logger)
    root.mainloop()


if __name__ == "__main__":
    main()
