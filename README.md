# PocketFlight

**Smartphone IMU-Controlled Drone System with Flood Monitoring**

[![ROS](https://img.shields.io/badge/ROS-Noetic-blue)](http://wiki.ros.org/noetic)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-GPL--3.0-red)](LICENSE)
[![Gazebo](https://img.shields.io/badge/Gazebo-11-orange)](http://gazebosim.org/)

---

## Overview

PocketFlight enables intuitive UAV teleoperation using your smartphone as a controller. By tilting and rotating your phone, you can pilot a quadcopter drone in real-time through its built-in IMU sensors (accelerometer and gyroscope).

The system was designed for scenarios where visual feedback may be limited or operators need intuitive control in challenging environments, such as flood monitoring in disaster zones.

---

## Features

- **Real-time drone control** via smartphone IMU (accelerometer & gyroscope)
- **PID-based altitude stabilization** with automatic takeoff sequence
- **Low-pass filtering** for smooth, responsive control
- **Gazebo simulation** support with Hector Quadrotor
- **Flood detection** using computer vision (HSV color segmentation)
- **Multi-drone support** (scalable up to 16 drones)
- **WebSocket-based** sensor data streaming from Android devices
- **Configurable parameters** via config file

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
┌─────────────────┐                     ┌───────────────────┐
│  Gazebo/Real    │ ◄─────────────────  │     drone01       │
│     Drone       │     UDP Commands    │   (ROS Node)      │
└─────────────────┘                     └───────────────────┘
```

### Data Flow

1. **Smartphone** streams accelerometer and gyroscope data via WebSocket
2. **imu_publisher** receives data and publishes to ROS topics
3. **controller** processes IMU data, applies filtering and PID control
4. **drone01** receives velocity commands and controls the drone
5. **Gazebo** simulates drone physics and environment

---

## Prerequisites

### Hardware
- Ubuntu 20.04 LTS (recommended)
- Android smartphone with accelerometer and gyroscope
- PC and smartphone on the same WiFi network

### Software
- [ROS Noetic](http://wiki.ros.org/noetic/Installation)
- [Gazebo 11](http://gazebosim.org/)
- Python 3.8+
- [SensorServer](https://play.google.com/store/apps/details?id=github.umer0586.sensorserver) Android app

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YarikMaydebura/Pocket-Flight-IMU-base-UAV-s-control-system.git
cd Pocket-Flight-IMU-base-UAV-s-control-system
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install ROS Dependencies

```bash
# Install Hector Quadrotor (if not already installed)
sudo apt-get install ros-noetic-hector-quadrotor-demo

# Install other dependencies
sudo apt-get install ros-noetic-gazebo-ros ros-noetic-cv-bridge
```

### 4. Setup Catkin Workspace

```bash
# Create workspace if it doesn't exist
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src

# Copy PocketFlight files
cp -r /path/to/PocketFlight/src/* flood_monitor_16/src/
cp -r /path/to/PocketFlight/launch/* flood_monitor_16/launch/
cp -r /path/to/PocketFlight/config/* flood_monitor_16/src/

# Build
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

### 5. Configure Smartphone IP

Edit `src/imu_publisher.py` and update the IP address:

```python
# Change this to your smartphone's IP address
ws_acc = websocket.WebSocketApp("ws://YOUR_PHONE_IP:8080/sensor/connect?type=android.sensor.accelerometer", ...)
ws_gyro = websocket.WebSocketApp("ws://YOUR_PHONE_IP:8080/sensor/connect?type=android.sensor.gyroscope", ...)
```

---

## Usage

### 1. Start SensorServer on Your Phone

1. Install [SensorServer](https://play.google.com/store/apps/details?id=github.umer0586.sensorserver) from Google Play
2. Open the app and note the IP address shown
3. Start the WebSocket server

### 2. Connect to Same Network

Ensure your PC and smartphone are connected to the same WiFi network.

### 3. Launch the System

```bash
# Source ROS workspace
source ~/catkin_ws/devel/setup.bash

# Launch the complete system
roslaunch flood_monitor_16 start.launch
```

### 4. Control the Drone

- **Tilt phone forward** → Drone moves forward
- **Tilt phone backward** → Drone moves backward
- **Tilt phone left** → Drone moves left
- **Tilt phone right** → Drone moves right
- **Rotate phone (yaw)** → Drone rotates

The drone will automatically take off to 2 meters altitude when the system starts.

---

## ROS Topics

| Topic | Message Type | Description |
|-------|--------------|-------------|
| `/phone_imu_acc` | `sensor_msgs/Imu` | Smartphone accelerometer data |
| `/phone_imu_gyro` | `sensor_msgs/Imu` | Smartphone gyroscope data |
| `/drone01/cmd_vel` | `geometry_msgs/Twist` | Velocity commands to drone |
| `/drone01/flood_status` | `std_msgs/Int32` | Flood detection status (0/1) |
| `/drone01/moments` | `std_msgs/Float32MultiArray` | Image moments for tracking |
| `/gazebo/model_states` | `gazebo_msgs/ModelStates` | Drone position from simulation |

---

## Configuration

Edit `config/config.ini` to tune system parameters:

```ini
[velocity]
h_vel_scale = -0.2    # Horizontal velocity scaling
v_vel_scale = -2      # Vertical velocity scaling

[position]
ceiling_height = 14   # Maximum flight height (meters)
monitor_height = 56   # Monitoring altitude

[color_range]
# HSV color range for flood detection
lower_H = 95
upper_H = 104
lower_S = 110
upper_S = 177
lower_V = 30
upper_V = 255

[flood_threshold]
value = 30            # Flood detection threshold (%)
```

### Controller Parameters (in controller.py)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TAKEOFF_ALTITUDE` | 2.0 m | Target takeoff altitude |
| `MINIMUM_ALTITUDE` | 1.0 m | Safety minimum altitude |
| `TAKEOFF_SPEED` | 0.5 m/s | Ascent speed |
| `FILTER_ALPHA` | 0.2 | Low-pass filter smoothing factor |
| `DEADBAND_THRESHOLD` | 0.2 | Ignore small IMU changes |
| `ALTITUDE_KP` | 0.5 | PID proportional gain |
| `ALTITUDE_KI` | 0.1 | PID integral gain |
| `ALTITUDE_KD` | 0.05 | PID derivative gain |

---

## Project Structure

```
PocketFlight/
├── README.md               # This file
├── LICENSE                 # GPL-3.0 License
├── .gitignore              # Git ignore rules
├── CONTRIBUTING.md         # Contribution guidelines
├── requirements.txt        # Python dependencies
│
├── src/                    # Source code
│   ├── imu_publisher.py    # IMU data publisher node
│   ├── controller.py       # Drone controller with PID
│   └── drone01.py          # Drone interface & flood detection
│
├── launch/                 # ROS launch files
│   ├── start.launch        # Main launch file
│   └── flood_monitor.launch # Simulation environment
│
├── config/                 # Configuration files
│   └── config.ini          # System parameters
│
├── docs/                   # Documentation
│   ├── installation.md     # Detailed installation guide
│   ├── usage.md            # Usage instructions
│   └── architecture.md     # System architecture details
│
└── demos/                  # Demo materials
    └── README.md           # Demo video links
```

---

## Demo

Demo videos coming soon! Check the [demos/](demos/) folder for video links.

---

## Troubleshooting

### WebSocket Connection Failed
- Ensure phone and PC are on the same network
- Check firewall settings on your PC
- Verify the IP address in `imu_publisher.py`

### Drone Not Responding
- Check if all ROS nodes are running: `rosnode list`
- Verify topics are publishing: `rostopic echo /phone_imu_acc`
- Check Gazebo is running properly

### Jerky Drone Movement
- Increase `FILTER_ALPHA` for more smoothing (max 1.0)
- Increase `DEADBAND_THRESHOLD` to ignore small movements

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

This means:
- You can use, modify, and distribute this code
- If you distribute modified versions, you must also use GPL-3.0
- You must give credit to the original authors
- You must disclose source code of derivative works

---

## Author

- **Maydebura Yaroslav** (YarikMaydebura) - yaroslav0523@gmail.com

---

## Acknowledgments

- Hector Quadrotor ROS package developers
- SensorServer Android app developers
- OpenCV community

---

## References

- [ROS Noetic Documentation](http://wiki.ros.org/noetic)
- [Hector Quadrotor Package](http://wiki.ros.org/hector_quadrotor)
- [Gazebo Simulation](http://gazebosim.org/)
- [SensorServer App](https://github.com/umer0586/SensorServer)

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
