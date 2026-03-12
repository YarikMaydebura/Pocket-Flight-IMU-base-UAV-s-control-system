# PocketFlight

**Smartphone IMU-Controlled Drone System**

[![ROS](https://img.shields.io/badge/ROS-Noetic-blue)](http://wiki.ros.org/noetic)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-GPL--3.0-red)](LICENSE)
[![Gazebo](https://img.shields.io/badge/Gazebo-11-orange)](http://gazebosim.org/)

---

## Overview

PocketFlight enables intuitive UAV teleoperation using your smartphone as a controller. By tilting and rotating your phone, you can pilot a quadcopter drone in real-time through its built-in IMU sensors (accelerometer and gyroscope).

The system streams sensor data over WiFi via WebSocket, processes it through configurable low-pass filtering and PID control, and outputs velocity commands to a simulated (Gazebo Hector Quadrotor) or real (DJI Tello) drone.

---

## Features

- **Real-time drone control** via smartphone IMU (accelerometer & gyroscope)
- **PID-based altitude stabilization** with automatic takeoff sequence
- **Low-pass filtering** for smooth, responsive control
- **Deadband threshold** to prevent drift from sensor noise
- **Gazebo simulation** support with Hector Quadrotor
- **DJI Tello** real hardware support
- **WebSocket-based** sensor data streaming from Android devices
- **Real-time data visualization** with matplotlib
- **Configurable parameters** via YAML config file

---

## System Architecture

```
┌─────────────────┐      WebSocket       ┌──────────────────┐
│   Smartphone    │ ──────────────────►  │  imu_publisher   │
│  (IMU Sensors)  │    192.168.x.x:8080  │     (ROS Node)   │
└─────────────────┘                      └────────┬─────────┘
                                                  │
                                    /phone_imu_acc & /phone_imu_gyro
                                                  │
                                                  ▼
                                         ┌───────────────┐
                                         │  controller   │
                                         │  (ROS Node)   │
                                         └───────┬───────┘
                                                 │
                                        /drone01/cmd_vel
                                                 │
                                                 ▼
                                        ┌───────────────────┐
                                        │  Gazebo / Tello   │
                                        │     (Drone)       │
                                        └───────────────────┘
```

### Data Flow

1. **Smartphone** streams accelerometer and gyroscope data via WebSocket
2. **imu_publisher** receives data and publishes to ROS topics
3. **controller** processes IMU data, applies low-pass filtering and PID altitude control
4. **Drone** receives velocity commands via `/drone01/cmd_vel` or `/tello/cmd_vel`

---

## Prerequisites

### Hardware
- Ubuntu 20.04 LTS (recommended)
- Android smartphone with accelerometer and gyroscope
- PC and smartphone on the same WiFi network

### Software
- [ROS Noetic](http://wiki.ros.org/noetic/Installation)
- [Gazebo 11](http://gazebosim.org/) (for simulation)
- Python 3.8+
- [SensorServer](https://github.com/umer0586/SensorServer) Android app

---

## Installation

### 1. Install ROS Dependencies

```bash
sudo apt-get install ros-noetic-hector-quadrotor-demo
sudo apt-get install ros-noetic-gazebo-ros
sudo apt-get install ros-noetic-geometry-msgs ros-noetic-sensor-msgs ros-noetic-std-msgs
```

### 2. Setup Catkin Workspace

```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
git clone https://github.com/YarikMaydebura/Pocket-Flight-IMU-base-UAV-s-control-system.git pocketflight_imu
cd ~/catkin_ws
catkin_make
source devel/setup.bash
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
```

### 3. Install Python Dependencies

```bash
cd ~/catkin_ws/src/pocketflight_imu
pip install -r requirements.txt
```

### 4. Make Scripts Executable

```bash
chmod +x src/*.py
```

### 5. Configure Smartphone IP

Edit `src/imu_publisher.py` and update the IP address to match your phone:

```python
ws_acc = websocket.WebSocketApp("ws://YOUR_PHONE_IP:8080/sensor/connect?type=android.sensor.accelerometer", ...)
ws_gyro = websocket.WebSocketApp("ws://YOUR_PHONE_IP:8080/sensor/connect?type=android.sensor.gyroscope", ...)
```

Or update `config/imu_control.yaml`:

```yaml
phone:
  ip: "YOUR_PHONE_IP"
  port: 8080
```

---

## Usage

### Gazebo Simulation

```bash
# Start SensorServer on your phone first, then:
roslaunch pocketflight_imu start.launch
```

### DJI Tello (Real Hardware)

```bash
roslaunch pocketflight_imu tello_control.launch
```

### Data Visualization

In a separate terminal:

```bash
rosrun pocketflight_imu data_visualizer.py
```

### Flight Controls

| Phone Motion | Drone Response |
|--------------|----------------|
| Tilt forward | Fly forward |
| Tilt backward | Fly backward |
| Tilt left | Fly left |
| Tilt right | Fly right |
| Rotate (yaw) | Rotate drone |

The drone automatically takes off to 2.0 meters altitude when the system starts.

---

## ROS Topics

| Topic | Message Type | Description |
|-------|--------------|-------------|
| `/phone_imu_acc` | `sensor_msgs/Imu` | Smartphone accelerometer data |
| `/phone_imu_gyro` | `sensor_msgs/Imu` | Smartphone gyroscope data |
| `/drone01/cmd_vel` | `geometry_msgs/Twist` | Velocity commands (Gazebo) |
| `/tello/cmd_vel` | `geometry_msgs/Twist` | Velocity commands (Tello) |

---

## Configuration

Tune parameters in `config/imu_control.yaml` or directly in `src/controller.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TAKEOFF_ALTITUDE` | 2.0 m | Target takeoff altitude |
| `MINIMUM_ALTITUDE` | 1.0 m | Safety minimum altitude |
| `TAKEOFF_SPEED` | 0.5 m/s | Ascent speed |
| `FILTER_ALPHA` | 0.2 | Low-pass filter smoothing (0=smooth, 1=raw) |
| `DEADBAND_THRESHOLD` | 0.2 | Ignore small IMU changes |
| `ALTITUDE_KP` | 0.5 | PID proportional gain |
| `ALTITUDE_KI` | 0.1 | PID integral gain |
| `ALTITUDE_KD` | 0.05 | PID derivative gain |

---

## Project Structure

```
pocketflight_imu/
├── README.md
├── LICENSE
├── .gitignore
├── CONTRIBUTING.md
├── CMakeLists.txt
├── package.xml
├── requirements.txt
├── config/
│   └── imu_control.yaml
├── demos/
│   └── README.md
├── docs/
│   ├── architecture.md
│   ├── installation.md
│   └── usage.md
├── launch/
│   ├── start.launch
│   └── tello_control.launch
├── research/
│   └── (research papers)
├── src/
│   ├── imu_publisher.py
│   ├── controller.py
│   ├── tello_controller.py
│   ├── hector_control.py
│   └── data_visualizer.py
└── videos/
    └── (demo videos)
```

---

## Troubleshooting

### WebSocket Connection Failed
- Ensure phone and PC are on the same WiFi network
- Check firewall settings on your PC
- Verify the IP address in `imu_publisher.py`

### Drone Not Responding
- Check if all ROS nodes are running: `rosnode list`
- Verify topics are publishing: `rostopic echo /phone_imu_acc`

### Jerky Drone Movement
- Decrease `FILTER_ALPHA` for more smoothing
- Increase `DEADBAND_THRESHOLD` to ignore small movements

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

---

## Author

- **Maydebura Yaroslav** (YarikMaydebura) - yaroslav0523@gmail.com

---

## Acknowledgments

- Hector Quadrotor ROS package developers
- SensorServer Android app developers

---

## Citation

If you use this project in your research, please cite:

```bibtex
@software{pocketflight2024,
  author = {Maydebura, Yaroslav},
  title = {PocketFlight: Smartphone IMU-Controlled Drone System},
  year = {2024},
  url = {https://github.com/YarikMaydebura/Pocket-Flight-IMU-base-UAV-s-control-system}
}
```
