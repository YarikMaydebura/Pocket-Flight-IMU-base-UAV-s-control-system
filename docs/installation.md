# Installation Guide

Detailed instructions for installing PocketFlight and all its dependencies.

---

## System Requirements

### Hardware
- **PC**: Ubuntu 20.04 LTS, 8GB+ RAM, dedicated GPU recommended for Gazebo
- **Smartphone**: Android 5.0+, accelerometer and gyroscope sensors, WiFi

### Software
- ROS Noetic
- Gazebo 11 (included with ROS desktop-full)
- Python 3.8+

---

## 1. Install ROS Noetic

```bash
# Setup sources
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'

# Setup keys
sudo apt install curl
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -

# Install
sudo apt update
sudo apt install ros-noetic-desktop-full

# Environment setup
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Dependencies
sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential
sudo rosdep init
rosdep update
```

---

## 2. Install Hector Quadrotor

```bash
sudo apt-get install ros-noetic-hector-quadrotor-demo
sudo apt-get install ros-noetic-hector-gazebo-plugins
sudo apt-get install ros-noetic-hector-models
```

---

## 3. Install ROS Packages

```bash
sudo apt-get install ros-noetic-gazebo-ros
sudo apt-get install ros-noetic-geometry-msgs
sudo apt-get install ros-noetic-sensor-msgs
sudo apt-get install ros-noetic-std-msgs
```

---

## 4. Setup PocketFlight

### Create Catkin Workspace

```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/
catkin_make
source devel/setup.bash
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
```

### Clone PocketFlight

```bash
cd ~/catkin_ws/src
git clone https://github.com/YarikMaydebura/Pocket-Flight-IMU-base-UAV-s-control-system.git pocketflight_imu
```

### Install Python Dependencies

```bash
cd ~/catkin_ws/src/pocketflight_imu
pip install -r requirements.txt
```

### Make Scripts Executable

```bash
chmod +x src/*.py
```

### Build Workspace

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

---

## 5. Smartphone Setup

### Install SensorServer App

1. Install **SensorServer** from [Google Play](https://play.google.com/store/apps/details?id=github.umer0586.sensorserver) or [GitHub](https://github.com/umer0586/SensorServer)
2. Grant required permissions (location, sensors)
3. Open the app and note the IP address displayed

### Network Configuration

1. Connect both PC and smartphone to the same WiFi network
2. Test connectivity: `ping YOUR_PHONE_IP`
3. Update `src/imu_publisher.py` with your phone's IP address

---

## 6. Verification

```bash
# Test ROS
roscore

# Test Gazebo (Ctrl+C to stop)
gazebo

# Test Hector Quadrotor (Ctrl+C to stop)
roslaunch hector_quadrotor_demo outdoor_flight_gazebo.launch

# Test WebSocket connection (with SensorServer running on phone)
cd ~/catkin_ws/src/pocketflight_imu
python3 src/imu_publisher.py
```

---

## Troubleshooting

- **ROS not found**: `source /opt/ros/noetic/setup.bash && source ~/catkin_ws/devel/setup.bash`
- **Python module not found**: `pip install -r requirements.txt`
- **Cannot connect to smartphone**: Check firewall, verify same WiFi network, restart SensorServer
- **Gazebo crashes**: Update graphics drivers (`sudo apt update && sudo apt upgrade`)

---

## Next Steps

After successful installation, proceed to the [Usage Guide](usage.md).
