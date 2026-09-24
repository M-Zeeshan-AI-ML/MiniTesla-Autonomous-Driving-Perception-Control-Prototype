import cv2
import numpy as np

class LaneDetector:
    def __init__(self, cfg: dict):
        self.low = int(cfg.get("canny_low", 50))
        self.high = int(cfg.get("canny_high", 150))
        self.roi_top = float(cfg.get("roi_top", 0.58))
        self.roi_bottom = float(cfg.get("roi_bottom", 0.98))
        self.min_line_length = int(cfg.get("min_line_length", 30))
        self.max_line_gap = int(cfg.get("max_line_gap", 40))

    def _roi(self, edges):
        h, w = edges.shape[:2]
        mask = np.zeros_like(edges)
        polygon = np.array([[
            (int(0.05*w), int(self.roi_bottom*h)),
            (int(0.42*w), int(self.roi_top*h)),
            (int(0.58*w), int(self.roi_top*h)),
            (int(0.95*w), int(self.roi_bottom*h))
        ]], dtype=np.int32)
        cv2.fillPoly(mask, polygon, 255)
        return cv2.bitwise_and(edges, mask)

    def detect(self, frame):
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, self.low, self.high)
        roi = self._roi(edges)

        lines = cv2.HoughLinesP(
            roi, 1, np.pi/180, threshold=30,
            minLineLength=self.min_line_length,
            maxLineGap=self.max_line_gap
        )

        left, right = [], []
        if lines is not None:
            for x1, y1, x2, y2 in lines.reshape(-1, 4):
                dx = x2 - x1
                dy = y2 - y1
                if dx == 0:
                    continue
                slope = dy / dx
                if abs(slope) < 0.35 or abs(slope) > 4:
                    continue
                if slope < 0 and max(x1, x2) < w * 0.62:
                    left.append((x1, y1, x2, y2))
                elif slope > 0 and min(x1, x2) > w * 0.38:
                    right.append((x1, y1, x2, y2))

        lane_center = None
        segments = []

        def averaged_line(items):
            if not items:
                return None
            xs, ys = [], []
            for x1, y1, x2, y2 in items:
                xs += [x1, x2]
                ys += [y1, y2]
            m, b = np.polyfit(xs, ys, 1)
            y_bottom = h * self.roi_bottom
            y_top = h * self.roi_top
            if abs(m) < 1e-6:
                return None
            x_bottom = int((y_bottom - b) / m)
            x_top = int((y_top - b) / m)
            return (x_bottom, int(y_bottom), x_top, int(y_top))

        l = averaged_line(left)
        r = averaged_line(right)

        if l:
            segments.append(l)
        if r:
            segments.append(r)

        if l and r:
            lane_center = int((l[0] + r[0]) / 2)
        elif l:
            lane_center = int(l[0] + w * 0.25)
        elif r:
            lane_center = int(r[0] - w * 0.25)

        return {
            "lane_center_x": lane_center,
            "frame_center_x": w // 2,
            "offset_px": None if lane_center is None else lane_center - w/2,
            "lines": segments,
            "edges": edges,
        }

    @staticmethod
    def draw(frame, result):
        out = frame.copy()
        for x1, y1, x2, y2 in result["lines"]:
            cv2.line(out, (x1,y1), (x2,y2), (255,255,255), 4)
        cx = result["frame_center_x"]
        cv2.line(out, (cx, 0), (cx, out.shape[0]), (200,200,200), 1)
        if result["lane_center_x"] is not None:
            lx = int(result["lane_center_x"])
            cv2.circle(out, (lx, int(out.shape[0]*0.75)), 8, (255,255,255), -1)
        return out
