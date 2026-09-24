import time
import cv2

from .lane import LaneDetector
from .perception import ObjectDetector
from .controller import PIDController, SafetyController

class VideoAgent:
    def __init__(self, cfg):
        self.cfg = cfg
        self.lane = LaneDetector(cfg["lane"])
        self.detector = ObjectDetector(cfg["perception"])
        self.controller = PIDController(cfg["controller"])
        self.safety = SafetyController(cfg["safety"])

    def process(self, frame):
        start = time.perf_counter()

        lane_result = self.lane.detect(frame)
        detections = self.detector.detect(frame)
        steering = self.controller.update(lane_result["offset_px"])
        brake = self.safety.should_brake(detections, frame.shape)

        annotated = self.lane.draw(frame, lane_result)
        annotated = self.detector.draw(annotated, detections)

        if brake:
            cv2.rectangle(
                annotated, (0,0),
                (annotated.shape[1]-1, annotated.shape[0]-1),
                (255,255,255), 8
            )
            cv2.putText(
                annotated, "SAFETY BRAKE",
                (30,55), cv2.FONT_HERSHEY_SIMPLEX,
                1.2, (255,255,255), 3
            )

        offset = lane_result["offset_px"]
        status = f"offset={offset:.1f}px" if offset is not None else "offset=N/A"
        cv2.putText(
            annotated,
            f"{status}  steering={steering:.2f}",
            (20, annotated.shape[0]-25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255,255,255), 2
        )

        elapsed_ms = (time.perf_counter() - start) * 1000
        return annotated, {
            "lane_offset_px": offset,
            "steering": steering,
            "brake": int(brake),
            "num_detections": len(detections),
            "processing_ms": elapsed_ms,
        }
