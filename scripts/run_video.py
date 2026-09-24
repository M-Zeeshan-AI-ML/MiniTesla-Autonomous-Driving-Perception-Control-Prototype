import argparse
import sys
from pathlib import Path
import time
import cv2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mini_tesla.config import load_config
from mini_tesla.agent import VideoAgent
from mini_tesla.telemetry import TelemetryLogger

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--no-yolo", action="store_true")
    parser.add_argument("--no-display", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    if args.no_yolo:
        cfg["perception"]["enabled"] = False

    cap = cv2.VideoCapture(args.input)
    if not cap.isOpened():
        raise SystemExit(f"Could not open input: {args.input}")

    width = int(cfg["input"].get("resize_width", 960))
    fps = cap.get(cv2.CAP_PROP_FPS) or cfg["input"].get("output_fps", 20)

    out_dir = ROOT / "runs" / "latest"
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / "annotated.mp4"

    writer = None
    if cfg["run"].get("save_video", True):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(
            str(output_path), fourcc, float(fps), (width, width*9//16)
        )

    telemetry = TelemetryLogger(out_dir / "telemetry.csv")
    agent = VideoAgent(cfg)

    frame_idx = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.resize(frame, (width, width*9//16))
            annotated, stats = agent.process(frame)

            telemetry.log({
                "frame": frame_idx,
                "time_sec": frame_idx / float(fps),
                **stats
            })

            if writer:
                writer.write(annotated)

            if cfg["run"].get("display", True) and not args.no_display:
                cv2.imshow("MiniTesla - CARLA Free", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            frame_idx += 1

    finally:
        cap.release()
        if writer:
            writer.release()
        telemetry.close()
        cv2.destroyAllWindows()

    print(f"Done. Results: {out_dir}")

if __name__ == "__main__":
    main()
