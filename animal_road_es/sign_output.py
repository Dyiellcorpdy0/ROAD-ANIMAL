"""Управление сигналом дорожного знака.

В тестовом режиме — квадрат на экране (Tkinter Canvas).
В перспективе — GPIO/CAN через переопределение set_color.
"""
import logging

logger = logging.getLogger(__name__)

COLOR_HEX = {
    "green": "#2ecc71",
    "yellow": "#f1c40f",
    "red": "#e74c3c",
}


class SignOutput:
    def __init__(self, canvas, rect_id):
        self.canvas = canvas
        self.rect_id = rect_id

    def set_color(self, color: str):
        """Устанавливает цвет лампы: green / yellow / red."""
        hex_color = COLOR_HEX.get(color, "#cccccc")
        try:
            self.canvas.itemconfig(self.rect_id, fill=hex_color)
        except Exception as e:  # noqa: BLE001
            logger.warning("Не удалось изменить цвет лампы: %s", e)

    # Заготовка под реальное железо
    def set_color_hardware(self, color: str):
        """TODO: RPi.GPIO / python-can."""
        pass
