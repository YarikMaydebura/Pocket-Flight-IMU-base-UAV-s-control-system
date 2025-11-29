# Installation Guide

This guide provides detailed instructions for installing PocketFlight and all its dependencies.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installing ROS Noetic](#installing-ros-noetic)
3. [Installing Gazebo](#installing-gazebo)
4. [Installing Hector Quadrotor](#installing-hector-quadrotor)
5. [Installing PocketFlight](#installing-pocketflight)
6. [Smartphone Setup](#smartphone-setup)
7. [Network Configuration](#network-configuration)
8. [Verification](#verification)

---

## System Requirements

### Hardware
- **PC**:
  - CPU: Intel i5 or equivalent (quad-core recommended)
  - RAM: 8GB minimum, 16GB recommended
  - GPU: Dedicated GPU recommended for Gazebo simulation
  - WiFi adapter

- **Smartphone**:
  - Android 5.0 or higher
  - IMU sensors (accelerometer and gyroscope)
  - WiFi capability

### Software
- **Operating System**: Ubuntu 20.04 LTS (Focal Fossa)
- **ROS**: Noetic Ninjemys
- **Python**: 3.8+
- **Gazebo**: 11

---

## Installing ROS Noetic

### 1. Setup sources.list

```bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
```

### 2. Setup keys

```bash
sudo apt install curl
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
```

### 3. Install ROS Noetic

```bash
sudo apt update
sudo apt install ros-noetic-desktop-full
```

### 4. Environment Setup

```bash
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 5. Install Dependencies

```bash
sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential
```

### 6. Initialize rosdep

```bash
sudo rosdep init
rosdep update
```

---

## Installing Gazebo

Gazebo 11 is included with ROS Noetic desktop-full installation. Verify installation:

```bash
gazebo --version
```

If not installed:

```bash
sudo apt install gazebo11 libgazebo11-dev
```

---

## Installing Hector Quadrotor

### 1. Install Hector Quadrotor packages

```bash
sudo apt-get install ros-noetic-hector-quadrotor-demo
sudo apt-get install ros-noetic-hector-gazebo-plugins
sudo apt-get install ros-noetic-hector-models
```

### 2. Install additional ROS packages

```bash
sudo apt-get install ros-noetic-gazebo-ros
sudo apt-get install ros-noetic-cv-bridge
sudo apt-get install ros-noetic-geometry-msgs
sudo apt-get install ros-noetic-sensor-msgs
sudo apt-get install ros-noetic-std-msgs
```

---

## Installing PocketFlight

### 1. Create Catkin Workspace

If you don't have a catkin workspace:

```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/
catkin_make
source devel/setup.bash
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
```

### 2. Clone PocketFlight

```bash
cd ~/catkin_ws/src
git clone https://github.com/YourUsername/PocketFlight.git
```

### 3. Create flood_monitor_16 Package

```bash
cd ~/catkin_ws/src
catkin_create_pkg flood_monitor_16 rospy std_msgs geometry_msgs sensor_msgs
```

### 4. Copy PocketFlight Files

```bash
cd ~/catkin_ws/src/flood_monitor_16

# Copy source files
cp ~/catkin_ws/src/PocketFlight/src/* src/

# Copy launch files
mkdir -p launch
cp ~/catkin_ws/src/PocketFlight/launch/* launch/

# Copy config file
cp ~/catkin_ws/src/PocketFlight/config/config.ini src/

# Make Python scripts executable
chmod +x src/*.py
```

### 5. Install Python Dependencies

```bash
cd ~/catkin_ws/src/PocketFlight
pip install -r requirements.txt
```

Or install individually:

```bash
pip install numpy
pip install opencv-python
pip install websocket-client
```

### 6. Build Workspace

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

---

## Smartphone Setup

### 1. Install SensorServer App

Install **SensorServer** from Google Play Store:
- Open Google Play Store
- Search for "SensorServer"
- Install the app by **umer0586**

Alternative: Download APK from [GitHub](https://github.com/umer0586/SensorServer)

### 2. Grant Permissions

When you first open SensorServer:
- Allow location permissions (required for sensor access)
- Allow overlay permissions if prompted

### 3. Configure SensorServer

1. Open SensorServer app
2. Note the IP address shown (e.g., 192.168.1.100)
3. Ensure WiFi is enabled
4. Keep the app open while using PocketFlight

---

## Network Configuration

### 1. Connect to Same Network

Ensure both your PC and smartphone are connected to the same WiFi network:

```bash
# Check PC IP address
ifconfig
# or
ip addr show
```

### 2. Test Connectivity

From your PC, ping the smartphone:

```bash
ping PHONE_IP_ADDRESS
```

Example:
```bash
ping 192.168.1.100
```

You should see responses. Press Ctrl+C to stop.

### 3. Update imu_publisher.py

Edit the smartphone IP in the code:

```bash
cd ~/catkin_ws/src/flood_monitor_16/src
nano imu_publisher.py
```

Find these lines and update the IP:

```python
ws_acc = websocket.WebSocketApp("ws://YOUR_PHONE_IP:8080/sensor/connect?type=android.sensor.accelerometer", ...)
ws_gyro = websocket.WebSocketApp("ws://YOUR_PHONE_IP:8080/sensor/connect?type=android.sensor.gyroscope", ...)
```

Replace `YOUR_PHONE_IP` with your smartphone's IP address.

---

## Verification

### 1. Test ROS Installation

```bash
roscore
```

You should see ROS master starting. Press Ctrl+C to stop.

### 2. Test Gazebo

```bash
gazebo
```

Gazebo should open. Close it after verification.

### 3. Test Hector Quadrotor

```bash
roslaunch hector_quadrotor_demo outdoor_flight_gazebo.launch
```

You should see a drone in Gazebo. Press Ctrl+C to stop.

### 4. Test WebSocket Connection

With SensorServer running on your phone:

```bash
cd ~/catkin_ws/src/flood_monitor_16/src
python3 imu_publisher.py
```

You should see WebSocket connection established messages.

---

## Troubleshooting

### ROS not found

```bash
source /opt/ros/noetic/setup.bash
source ~/catkin_ws/devel/setup.bash
```

### Python module not found

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Gazebo crashes

```bash
# Update graphics drivers
sudo apt update
sudo apt upgrade
```

### Cannot connect to smartphone

- Check firewall settings
- Ensure both devices on same network
- Verify smartphone IP hasn't changed
- Restart SensorServer app

---

## Next Steps

After successful installation, proceed to [Usage Guide](usage.md) to learn how to fly your drone!
