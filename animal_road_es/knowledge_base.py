"""Загрузка онтологии (OWL) и правил (JSON)."""
import json
import os
import logging

logger = logging.getLogger(__name__)


class KnowledgeBase:
    def __init__(self, ontology_path: str, rules_path: str):
        self.ontology_path = ontology_path
        self.rules_path = rules_path
        self.ontology = None
        self.rules = []
        self.animal_classes = []

        self._load_ontology()
        self._load_rules()

    def _load_ontology(self):
        """Пытается загрузить OWL-онтологию, если есть owlready2 и файл."""
        if not os.path.exists(self.ontology_path):
            logger.warning("Онтология не найдена: %s", self.ontology_path)
            return
        try:
            from owlready2 import get_ontology
            self.ontology = get_ontology(self.ontology_path).load()
            self.animal_classes = [
                cls.name for cls in self.ontology.Animal.descendants()
            ]
            logger.info("Онтология загружена: %s", self.animal_classes)
        except Exception as e:  # noqa: BLE001
            logger.warning("Не удалось загрузить онтологию: %s", e)

    def _load_rules(self):
        """Загружает продукционные правила из JSON."""
        with open(self.rules_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.rules = sorted(
            data.get("rules", []),
            key=lambda r: r.get("priority", 0),
            reverse=True,
        )
        logger.info("Загружено правил: %d", len(self.rules))
