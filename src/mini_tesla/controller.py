class PIDController:
    def __init__(self, cfg: dict):
        self.kp = float(cfg.get("kp", 0.015))
        self.ki = float(cfg.get("ki", 0.0005))
        self.kd = float(cfg.get("kd", 0.008))
        self.max_steering = float(cfg.get("max_steering", 1.0))
        self.integral = 0.0
        self.previous_error = 0.0

    def update(self, error_px):
        if error_px is None:
            return 0.0
        error = float(error_px)
        self.integral += error
        derivative = error - self.previous_error
        self.previous_error = error
        value = self.kp*error + self.ki*self.integral + self.kd*derivative
        return max(-self.max_steering, min(self.max_steering, value))

class SafetyController:
    def __init__(self, cfg: dict):
        self.enabled = bool(cfg.get("enabled", True))
        self.classes = set(cfg.get("classes", []))
        self.center_margin = float(cfg.get("center_margin", 0.28))
        self.min_box_area_ratio = float(cfg.get("min_box_area_ratio", 0.035))

    def should_brake(self, detections, frame_shape):
        if not self.enabled:
            return False
        h, w = frame_shape[:2]
        frame_area = h*w
        left_limit = w*(0.5-self.center_margin)
        right_limit = w*(0.5+self.center_margin)

        for d in detections:
            if d["label"] not in self.classes:
                continue
            x1,y1,x2,y2 = d["bbox"]
            area_ratio = max(0, x2-x1) * max(0, y2-y1) / frame_area
            center_x = (x1+x2)/2
            if area_ratio >= self.min_box_area_ratio and left_limit <= center_x <= right_limit:
                return True
        return False
