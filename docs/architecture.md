# Architecture

## CARLA-free architecture

```text
Driving Video / Image
        |
        v
 OpenCV Frame Reader
        |
        +--------------------+
        |                    |
        v                    v
  Lane Detection       YOLO Object Detection
        |                    |
        +---------+----------+
                  |
                  v
           Safety Controller
                  |
                  v
            PID Controller
                  |
                  v
        Steering / Brake Signal
                  |
                  v
       Annotated Video + CSV
```

## What is simulated

Because this version has no vehicle simulator, steering and braking are **computed control signals**, not commands sent to a real or simulated car.

## Future CARLA upgrade

A later version can replace the video reader with CARLA camera frames and replace computed control signals with CARLA vehicle control commands.
