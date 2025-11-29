# System Architecture

This document provides a comprehensive technical overview of the PocketFlight system architecture.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [ROS Topic Structure](#ros-topic-structure)
6. [Control Loop](#control-loop)
7. [Design Decisions](#design-decisions)

---

## System Overview

PocketFlight is a **modular ROS-based drone control system** that uses smartphone IMU sensors as the input device. The architecture follows the standard robotics paradigm of separating **sensing**, **decision-making**, and **actuation** into distinct components.

### Key Principles

- **Modularity**: Each component is independent and communicates via ROS topics
- **Real-time**: Low-latency sensor data streaming and control
- **Scalability**: Designed to support multiple drones
- **Extensibility**: Easy to add new features (sensors, algorithms, etc.)

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
                    WiFi Network (UDP)
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
│         │  - IMU data processing          │                    │
│         │  - Low-pass filtering           │                    │
│         │  - PID altitude control         │                    │
│         │  - Velocity command generation  │                    │
│         └──────────┬──────────────────────┘                    │
│                    │                                            │
│              /drone01/cmd_vel                                  │
│              (geometry_msgs/Twist)                             │
│                    │                                            │
│                    ▼                                            │
│         ┌─────────────────────────────────┐                    │
│         │     drone01.py (ROS Node)       │                    │
│         │  - Flood detection (OpenCV)     │                    │
│         │  - Position monitoring          │                    │
│         │  - Velocity execution           │                    │
│         └──────────┬──────────────────────┘                    │
│                    │                                            │
│              Gazebo topics                                     │
└────────────────────┼────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────────┐
│                   SIMULATION/HARDWARE LAYER                     │
│         ┌─────────────────────────────────┐                    │
│         │      Gazebo Simulator           │                    │
│         │  - Physics engine               │                    │
│         │  - Hector Quadrotor model       │                    │
│         │  - Environment rendering        │                    │
│         │  - Camera simulation            │                    │
│         └─────────────────────────────────┘                    │
└────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. imu_publisher.py

**Purpose**: Bridge between smartphone IMU sensors and ROS ecosystem

**Key Functions**:
- `on_message_acc()`: Handles incoming accelerometer data
- `on_message_gyro()`: Handles incoming gyroscope data
- `imu_publisher()`: Main ROS publisher loop

**Technology**:
- WebSocket client (websocket-client library)
- JSON parsing
- ROS sensor_msgs/Imu publisher

**Data Flow**:
```
Smartphone → WebSocket → JSON Parse → ROS Imu Message → Publish
```

**Published Topics**:
- `/phone_imu_acc` (sensor_msgs/Imu) - 20 Hz
- `/phone_imu_gyro` (sensor_msgs/Imu) - 20 Hz

**Error Handling**:
- WebSocket reconnection on disconnect
- JSON decode error catching
- Logging of connection status

---

### 2. controller.py

**Purpose**: Main control logic for drone flight based on IMU input

**Key Functions**:
- `imu_acc_callback()`: Process accelerometer readings
- `imu_gyro_callback()`: Process gyroscope readings
- `low_pass_filter()`: Smooth sensor data
- `takeoff()`: Autonomous takeoff sequence
- `pid_control_altitude()`: Altitude stabilization
- `run()`: Main control loop

**Control Algorithm**:

1. **Sensor Fusion**:
   - Combines accelerometer and gyroscope data
   - Subtracts gravity from z-axis acceleration

2. **Filtering**:
   - Low-pass filter with configurable alpha
   - Deadband threshold to ignore small movements

3. **PID Control**:
   - Proportional-Integral-Derivative for altitude
   - Maintains stable flight at desired height

4. **Velocity Mapping**:
   ```
   cmd_vel.linear.x = filtered_imu.x * SCALING
   cmd_vel.linear.y = filtered_imu.y * SCALING
   cmd_vel.linear.z = PID(altitude_error)
   cmd_vel.angular.z = filtered_gyro.z * SCALING
   ```

**Parameters**:
| Parameter | Default | Purpose |
|-----------|---------|---------|
| TAKEOFF_ALTITUDE | 2.0 m | Target altitude |
| FILTER_ALPHA | 0.2 | Low-pass filter weight |
| ALTITUDE_KP | 0.5 | PID proportional gain |
| ALTITUDE_KI | 0.1 | PID integral gain |
| ALTITUDE_KD | 0.05 | PID derivative gain |

**Subscribed Topics**:
- `/phone_imu_acc`
- `/phone_imu_gyro`

**Published Topics**:
- `/drone01/cmd_vel` (geometry_msgs/Twist) - 10 Hz

---

### 3. drone01.py

**Purpose**: Drone-specific interface for flood monitoring and position control

**Key Functions**:
- `image_callback()`: Process camera feed for flood detection
- `pos_callback()`: Receive target positions
- `callback()`: Monitor drone position from Gazebo

**Computer Vision**:
- **Color Space**: BGR → HSV conversion
- **Segmentation**: HSV range thresholding
- **Detection**: Pixel counting for flood percentage
- **Tracking**: Image moments calculation

**Flood Detection Algorithm**:
```python
1. Capture image from downward camera
2. Convert BGR to HSV color space
3. Apply color range mask (configurable)
4. Calculate flood percentage
5. Publish status if > threshold
```

**Configuration** (config.ini):
```ini
[color_range]
lower_H = 95   # Blue hue for water
upper_H = 104
lower_S = 110
upper_S = 177
lower_V = 30
upper_V = 255

[flood_threshold]
value = 30     # Percentage threshold
```

**Subscribed Topics**:
- `/drone01/downward_cam/camera/image`
- `/controller` (target positions)
- `/gazebo/model_states`

**Published Topics**:
- `/drone01/flood_status` (Int32)
- `/drone01/moments` (Float32MultiArray)
- `/drone01/cmd_vel` (Twist)

---

## Data Flow

### Startup Sequence

```
1. roslaunch start.launch
   │
   ├─→ Start ROS core
   │
   ├─→ Launch Gazebo + world
   │   └─→ Load Hector Quadrotor model
   │
   ├─→ Start imu_publisher node
   │   ├─→ Connect to WebSocket (smartphone)
   │   └─→ Begin publishing IMU data
   │
   └─→ Start controller node
       ├─→ Subscribe to IMU topics
       ├─→ Execute takeoff sequence
       └─→ Enter main control loop
```

### Runtime Data Flow

```
Smartphone IMU (50 Hz)
    │
    ▼
WebSocket (JSON)
    │
    ▼
imu_publisher (20 Hz)
    │
    ├─→ /phone_imu_acc
    └─→ /phone_imu_gyro
        │
        ▼
controller (10 Hz)
    │
    ├─→ Low-pass filter
    ├─→ PID altitude control
    └─→ Generate cmd_vel
        │
        ▼
drone01 or Gazebo
    │
    └─→ Execute movement
```

---

## ROS Topic Structure

### Topic Graph

```
/phone_imu_acc ──────┐
                     ├──→ controller ──→ /drone01/cmd_vel ──→ drone01/Gazebo
/phone_imu_gyro ─────┘

/gazebo/model_states ──→ drone01
                             │
                             ├──→ /drone01/flood_status
                             └──→ /drone01/moments
```

### Message Types

| Topic | Type | Fields |
|-------|------|--------|
| /phone_imu_acc | sensor_msgs/Imu | linear_acceleration (x,y,z) |
| /phone_imu_gyro | sensor_msgs/Imu | angular_velocity (x,y,z) |
| /drone01/cmd_vel | geometry_msgs/Twist | linear (x,y,z), angular (z) |
| /drone01/flood_status | std_msgs/Int32 | data (0 or 1) |
| /drone01/moments | std_msgs/Float32MultiArray | m00, m10, m01, m11, m20, m02 |

---

## Control Loop

### Frequency Analysis

| Component | Rate | Latency |
|-----------|------|---------|
| Smartphone sensors | ~50 Hz | <10 ms |
| WebSocket transmission | Variable | 20-50 ms |
| imu_publisher | 20 Hz | ~50 ms |
| controller | 10 Hz | ~100 ms |
| Gazebo physics | 1000 Hz | ~1 ms |

**Total latency**: ~200-300 ms (smartphone → drone response)

### Control Loop Diagram

```
     ┌─────────────────────────────────────┐
     │                                     │
     ▼                                     │
┌─────────┐    ┌──────────┐    ┌─────────┴────┐
│   IMU   │───→│Controller│───→│     Drone    │
│ Sensors │    │  (PID)   │    │   (Gazebo)   │
└─────────┘    └──────────┘    └──────────────┘
                    ▲                  │
                    │                  │
                    └──────────────────┘
                  Position feedback
```

---

## Design Decisions

### Why ROS?

- **Modularity**: Easy to swap components
- **Ecosystem**: Rich set of tools and packages
- **Debugging**: rostopic, rosnode for monitoring
- **Scalability**: Supports distributed systems

### Why WebSocket?

- **Real-time**: Low latency communication
- **Bidirectional**: Potential for future feedback
- **Standard**: Works with many platforms
- **Lightweight**: Minimal overhead

### Why Low-Pass Filter?

- **Noise Reduction**: Smartphone sensors are noisy
- **Smooth Control**: Prevents jerky movements
- **Safety**: Reduces risk of sudden commands

### Why PID for Altitude?

- **Stability**: Maintains desired height
- **Responsiveness**: Quick error correction
- **Tunability**: Easy to adjust gains

---

## Extensibility

### Adding New Sensors

```python
# In imu_publisher.py
def on_message_magnetometer(ws, message):
    # Process magnetometer data
    pass

ws_mag = websocket.WebSocketApp("ws://IP:8080/sensor/connect?type=magnetometer", ...)
```

### Adding Safety Features

```python
# In controller.py
def check_safe_bounds(position):
    if position.z < MINIMUM_ALTITUDE:
        return False
    if distance_from_origin(position) > MAX_RADIUS:
        return False
    return True
```

### Multi-Drone Coordination

Uncomment additional drones in `flood_monitor.launch` and implement coordination logic in a new node.

---

## References

- [ROS Architecture](http://wiki.ros.org/ROS/Concepts)
- [Hector Quadrotor Documentation](http://wiki.ros.org/hector_quadrotor)
- [WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- [PID Control Theory](https://en.wikipedia.org/wiki/PID_controller)
