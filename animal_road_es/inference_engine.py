"""Машина вывода: продукционный движок на правилах ЕСЛИ-ТО."""
import logging

logger = logging.getLogger(__name__)


class InferenceEngine:
    RISK_ORDER = {"low": 0, "medium": 1, "high": 2}

    def __init__(self, kb):
        self.kb = kb
        self.last_result = None

    def assess(self, detections: list) -> dict:
        """
        detections — список словарей:
            {"class": "лось", "confidence": 0.91,
             "position": "road"|"shoulder"|"none",
             "bbox": (x1, y1, x2, y2)}
        Возвращает:
            {"risk": "...", "color": "...", "rule_id": "...", "reason": "..."}
        """
        best = {
            "risk": "low",
            "color": "green",
            "rule_id": "R3",
            "reason": "Животных не обнаружено",
        }

        for det in detections:
            for rule in self.kb.rules:
                if self._matches(rule, det):
                    risk = rule["then"]["risk"]
                    if self.RISK_ORDER[risk] > self.RISK_ORDER[best["risk"]]:
                        best = {
                            "risk": risk,
                            "color": rule["then"]["color"],
                            "rule_id": rule["id"],
                            "reason": (
                                f"Обнаружен объект '{det['class']}' "
                                f"с уверенностью {det['confidence']:.2f}; "
                                f"положение = {det['position']}; "
                                f"сработало правило {rule['id']} "
                                f"({rule.get('description', '')})"
                            ),
                        }
        self.last_result = best
        return best

    def _matches(self, rule: dict, detection: dict) -> bool:
        condition = rule.get("if", {})
        for key, value in condition.items():
            if detection.get(key) != value:
                return False
        return True
