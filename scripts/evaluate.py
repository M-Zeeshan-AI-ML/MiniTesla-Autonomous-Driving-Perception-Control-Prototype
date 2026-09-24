import argparse
import pandas as pd

def main():
    p = argparse.ArgumentParser()
    p.add_argument("telemetry")
    args = p.parse_args()

    df = pd.read_csv(args.telemetry)
    print("\n=== MiniTesla Evaluation ===")
    print(f"Frames: {len(df)}")

    valid = df["lane_offset_px"].dropna()
    if len(valid):
        print(f"Mean absolute lane offset: {valid.abs().mean():.2f} px")
        print(f"Max absolute lane offset:  {valid.abs().max():.2f} px")
    else:
        print("Lane offset: no valid detections")

    print(f"Mean processing latency: {df.processing_ms.mean():.2f} ms")
    print(f"P95 processing latency:  {df.processing_ms.quantile(.95):.2f} ms")
    print(f"Safety-brake frames:     {int(df.brake.sum())}")

if __name__ == "__main__":
    main()
