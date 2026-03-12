# System Architecture

Technical overview of the PocketFlight IMU control system.

---

## Overview

PocketFlight is a **2-node ROS system** that uses smartphone IMU sensors to control a drone. The architecture separates **sensing** (imu_publisher) from **control** (controller), communicating via standard ROS topics.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        SMARTPHONE LAYER                         │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │ Accelerometer│   │  Gyroscope   │   │ SensorServer │       │
│  │  (Hardware)  │   │  (Hardware)  │   │     (App)    │       │
│  └───────┬──────┘   └───────┬──────┘   └───────┬──────┘       │
│          └──────────────┴─────────────────────┘               │
│                            │                                    │
│                      JSON/WebSocket                            │
│                            │ (Port 8080)                        │
└────────────────────────────┼────────────────────────────────────┘
                             │
                    WiFi Network
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                       ROS LAYER (PC)                            │
│                            ▼                                    │
│         ┌─────────────────────────────────┐                    │
│         │   imu_publisher.py (ROS Node)   │                    │
│         │  - WebSocket client             │                    │
│         │  - JSON parsing                 │                    │
│         │  - ROS message publishing       │                    │
│         └──────────┬──────────────────────┘                    │
│                    │                                            │
│         /phone_imu_acc    /phone_imu_gyro                      │
│         (sensor_msgs/Imu) (sensor_msgs/Imu)                    │
│                    │                                            │
│                    ▼                                            │
│         ┌─────────────────────────────────┐                    │
│         │    controller.py (ROS Node)     │                    │
│         │  - Low-pass filtering           │                    │
│         │  - PID altitude control         │                    │
│         │  - Velocity command generation  │                    │
│         └──────────┬──────────────────────┘                    │
│                    │                                            │
│              /drone01/cmd_vel                                  │
│              (geometry_msgs/Twist)                             │
│                    │                                            │
└────────────────────┼────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│                   SIMULATION/HARDWARE LAYER                     │
│         ┌─────────────────────────────────┐                    │
│         │   Gazebo (Hector Quadrotor)     │                    │
│         │        or DJI Tello             │                    │
│         └─────────────────────────────────┘                    │
└────────────────────────────────────────────────────────────────┘
```

---

## Node Details

### 1. imu_publisher.py

**Purpose**: Bridge between smartphone IMU sensors and ROS.

- Connects to Android SensorServer app via WebSocket
- Parses JSON sensor data (accelerometer + gyroscope)
- Publishes `sensor_msgs/Imu` messages at ~20 Hz

**Published Topics**:
- `/phone_imu_acc` — accelerometer (x, y, z)
- `/phone_imu_gyro` — gyroscope (x, y, z)

### 2. controller.py

**Purpose**: IMU-based drone flight control with PID altitude stabilization.

**Processing Pipeline**:

```
Raw IMU → Gravity Subtraction → Low-Pass Filter → Deadband → PID (altitude) → cmd_vel
```

1. **Gravity subtraction**: Removes 9.81 m/s² from z-axis acceleration
2. **Low-pass filter**: EMA smoothing with alpha=0.2
3. **Deadband**: Ignores values below 0.2 threshold
4. **PID altitude control**: Maintains stable flight height (KP=0.5, KI=0.1, KD=0.05)
5. **Velocity mapping**: IMU tilt → linear velocity, gyro yaw → angular velocity

**Subscribed Topics**: `/phone_imu_acc`, `/phone_imu_gyro`
**Published Topics**: `/drone01/cmd_vel`

---

## Tuning Constants

| Parameter | Default | Location | Purpose |
|-----------|---------|----------|---------|
| `TAKEOFF_ALTITUDE` | 2.0 m | controller.py | Target altitude |
| `FILTER_ALPHA` | 0.2 | controller.py | Low-pass filter weight |
| `DEADBAND_THRESHOLD` | 0.2 | controller.py | Noise gate |
| `ALTITUDE_KP` | 0.5 | controller.py | PID proportional gain |
| `ALTITUDE_KI` | 0.1 | controller.py | PID integral gain |
| `ALTITUDE_KD` | 0.05 | controller.py | PID derivative gain |
| `SPEED_SCALING_FACTOR` | 1.0 | controller.py | Velocity multiplier |

---

## Frequency Analysis

| Component | Rate | Latency |
|-----------|------|---------|
| Smartphone sensors | ~50 Hz | <10 ms |
| WebSocket transmission | Variable | 20-50 ms |
| imu_publisher | 20 Hz | ~50 ms |
| controller | 10 Hz | ~100 ms |
| Gazebo physics | 1000 Hz | ~1 ms |

**Total end-to-end latency**: ~200-300 ms

---

## Design Decisions

- **ROS**: Modular architecture, rich debugging tools (rostopic, rosnode), hardware abstraction
- **WebSocket**: Low-latency, bidirectional, works with SensorServer Android app
- **Low-pass filter**: Smartphone IMU sensors are noisy; EMA smoothing prevents jerky control
- **PID for altitude**: Maintains stable hover without manual z-axis input
- **Separate publisher/controller**: Allows swapping controllers (hector_control.py, tello_controller.py) without changing the sensor bridge

---

## References

- [ROS Architecture](http://wiki.ros.org/ROS/Concepts)
- [Hector Quadrotor Documentation](http://wiki.ros.org/hector_quadrotor)
- [WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [PID Control Theory](https://en.wikipedia.org/wiki/PID_controller)
