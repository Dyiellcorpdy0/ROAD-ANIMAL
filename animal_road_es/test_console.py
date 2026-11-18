"""Тестовый пульт (Tkinter)."""
import time
import tkinter as tk
from tkinter import ttk, messagebox

import cv2
import numpy as np
from PIL import Image, ImageTk

from sign_output import SignOutput


ZONE_COLORS = {
    "road": (0, 200, 0),        # зелёный контур (не путать с лампой)
    "shoulder": (0, 200, 255),  # жёлтый контур
}


class TestConsoleApp:
    def __init__(self, root, config, detector, engine, event_logger):
        self.root = root
        self.config = config
        self.detector = detector
        self.engine = engine
        self.logger = event_logger
        self.cap = self._open_source()
        self.red_lamp_until = 0.0  # таймер красного сигнала при обнаружении животного

        self._build_ui()
        self._schedule_next_frame()

    # ---------- Инициализация ----------
    def _open_source(self):
        src = self.config.get("video_source") or self.config["camera_index"]
        cap = cv2.VideoCapture(src)
        if not cap.isOpened():
            messagebox.showwarning(
                "Источник видео",
                "Не удалось открыть камеру. Работаем в демо-режиме (без видео)."
            )
        return cap

    def _build_ui(self):
        self.root.title("Тестовый пульт — Система распознавания животных")
        self.root.configure(bg="#1e1e1e")

        # Заголовок
        title = tk.Label(
            self.root,
            text="Тестовый пульт: Система распознавания животных на дороге",
            font=("Arial", 13, "bold"), fg="white", bg="#1e1e1e",
        )
        title.grid(row=0, column=0, columnspan=2, pady=6)

        # Видео
        self.video_label = tk.Label(self.root, bg="black")
        self.video_label.grid(row=1, column=0, padx=8, pady=8)

        # Лампа знака
        lamp_frame = tk.Frame(self.root, bg="#1e1e1e")
        lamp_frame.grid(row=1, column=1, padx=8, pady=8, sticky="n")
        tk.Label(
            lamp_frame, text="Лампа дорожного знака",
            fg="white", bg="#1e1e1e", font=("Arial", 11)
        ).pack(pady=4)
        self.lamp_canvas = tk.Canvas(
            lamp_frame, width=140, height=140, bg="#2d2d2d",
            highlightthickness=0,
        )
        self.lamp_canvas.pack()
        self.lamp_rect = self.lamp_canvas.create_oval(
            15, 15, 125, 125, fill="#2ecc71", outline="#111", width=3,
        )
        self.sign_output = SignOutput(self.lamp_canvas, self.lamp_rect)

        # Статус
        self.status_var = tk.StringVar(value="Ожидание...")
        tk.Label(
            self.root, textvariable=self.status_var,
            fg="white", bg="#1e1e1e", font=("Consolas", 11),
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=8)

    # ---------- Цикл обработки ----------
    def _schedule_next_frame(self):
        self.root.after(30, self._process_frame)

    def _process_frame(self):
        target_w = self.config["frame_width"]
        target_h = self.config["frame_height"]

        # Если источника нет — рисуем заглушку демо-режима
        if not (self.cap and self.cap.isOpened()):
            disp_frame = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            cv2.putText(
                disp_frame, "DEMO MODE — no video source",
                (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2,
            )
            ret = False
            detections = []
        else:
            ret, frame = self.cap.read()
            # Видеофайл дошёл до конца — зацикливаем: перематываем на начало
            if not ret or frame is None:
                src = self.config.get("video_source") or ""
                if src and str(src).isdigit() is False:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.cap.read()
                if not ret or frame is None:
                    disp_frame = np.zeros((target_h, target_w, 3), dtype=np.uint8)
                    cv2.putText(
                        disp_frame, "DEMO MODE — no video source",
                        (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2,
                    )
                    ret = False
                    detections = []
                    frame = None

            if frame is not None and ret:
                # Масштабируем пропорционально, без растяжения (letterboxing)
                orig_h, orig_w = frame.shape[:2]
                scale = min(target_w / orig_w, target_h / orig_h)
                new_w = max(1, int(orig_w * scale))
                new_h = max(1, int(orig_h * scale))
                frame_resized = cv2.resize(
                    frame, (new_w, new_h), interpolation=cv2.INTER_AREA
                )

                # Чёрный холст и вставка кадра по центру
                disp_frame = np.zeros((target_h, target_w, 3), dtype=np.uint8)
                x_off = (target_w - new_w) // 2
                y_off = (target_h - new_h) // 2
                disp_frame[y_off:y_off + new_h, x_off:x_off + new_w] = frame_resized

                # 1. Детекция на чистом видеокадре (без чёрных полос)
                detections = self.detector.detect(frame_resized)

                # Смещаем bbox под холст с учётом отступа
                for det in detections:
                    x1, y1, x2, y2 = det["bbox"]
                    det["bbox"] = (
                        x1 + x_off, y1 + y_off,
                        x2 + x_off, y2 + y_off,
                    )
            else:
                detections = []

        frame = disp_frame
        h, w = frame.shape[:2]

        # 2. Интерпретация положения
        detections = self._interp_positions(detections, (w, h))

        # 3. Машина вывода
        assessment = self.engine.assess(detections)

        # 4. Лампа — при обнаружении животного красный горит 5 секунд
        now = time.time()
        if detections:
            self.red_lamp_until = now + 5.0
        lamp_color = "red" if now < self.red_lamp_until else assessment["color"]
        self.sign_output.set_color(lamp_color)

        # 5. Лог
        self.logger.log(detections, assessment)

        # 6. Отрисовка
        frame = self._draw(frame, detections, assessment)

        # 7. Статус
        self.status_var.set(
            f"Риск: {assessment['risk'].upper():7s} | "
            f"Цвет: {lamp_color:6s} | "
            f"Правило: {assessment['rule_id']} | "
            f"Объектов: {len(detections)}"
        )

        # 8. Показ кадра
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgtk = ImageTk.PhotoImage(image=Image.fromarray(rgb))
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        self._schedule_next_frame()

    def _interp_positions(self, detections, frame_size):
        # Используем PositionInterpreter через engine
        from position_interpreter import PositionInterpreter
        interp = PositionInterpreter(self.config)
        return interp.interpret(detections, frame_size)

    def _draw(self, frame, detections, assessment):
        h, w = frame.shape[:2]

        # Bounding boxes
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            pos = det.get("position", "none")
            color = ZONE_COLORS.get(pos, (180, 180, 180))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"{det['class']} {det['confidence']:.2f} [{pos}]"
            cv2.putText(
                frame, label, (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2,
            )

        # Баннер
        banner = f"RISK: {assessment['risk'].upper()}  |  LAMP: {assessment['color'].upper()}"
        cv2.rectangle(frame, (0, h - 40), (w, h), (30, 30, 30), -1)
        cv2.putText(
            frame, banner, (12, h - 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
        )
        return frame

    @staticmethod
    def _draw_zone(frame, zone, color):
        h, w = frame.shape[:2]
        x1 = int(zone[0] * w); y1 = int(zone[1] * h)
        x2 = int(zone[2] * w); y2 = int(zone[3] * h)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)


