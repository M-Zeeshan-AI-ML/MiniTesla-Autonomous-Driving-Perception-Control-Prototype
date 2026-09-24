class ObjectDetector:
    def __init__(self, cfg: dict):
        self.enabled = bool(cfg.get("enabled", True))
        self.confidence = float(cfg.get("confidence", 0.35))
        self.model_name = cfg.get("model", "yolo11n.pt")
        self.model = None

        if self.enabled:
            from ultralytics import YOLO
            self.model = YOLO(self.model_name)

    def detect(self, frame):
        if not self.enabled or self.model is None:
            return []

        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            verbose=False
        )

        detections = []
        for result in results:
            names = result.names
            if result.boxes is None:
                continue
            for box in result.boxes:
                xyxy = box.xyxy[0].cpu().numpy().astype(int).tolist()
                conf = float(box.conf[0].cpu().item())
                cls_id = int(box.cls[0].cpu().item())
                label = names[cls_id]
                x1, y1, x2, y2 = xyxy
                detections.append({
                    "label": label,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2],
                })
        return detections

    @staticmethod
    def draw(frame, detections):
        import cv2
        out = frame.copy()
        for d in detections:
            x1, y1, x2, y2 = d["bbox"]
            text = f'{d["label"]} {d["confidence"]:.2f}'
            cv2.rectangle(out, (x1,y1), (x2,y2), (255,255,255), 2)
            cv2.putText(out, text, (x1, max(20,y1-6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 2)
        return out
