from src.mini_tesla.controller import PIDController, SafetyController

def test_pid_output_is_bounded():
    pid = PIDController({"kp": 1, "ki": 0, "kd": 0, "max_steering": 1})
    assert -1 <= pid.update(1000) <= 1
    assert -1 <= pid.update(-1000) <= 1

def test_safety_brake():
    safety = SafetyController({
        "enabled": True,
        "classes": ["car"],
        "center_margin": 0.28,
        "min_box_area_ratio": 0.01
    })
    detections = [{"label":"car", "confidence":0.9, "bbox":[400,200,600,500]}]
    assert safety.should_brake(detections, (720, 1280, 3)) is True
