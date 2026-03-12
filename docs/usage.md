# Usage Guide

How to use PocketFlight to control a drone with your smartphone.

---

## Pre-flight Checklist

- [ ] ROS Noetic is installed and sourced
- [ ] Catkin workspace is built and sourced
- [ ] Smartphone and PC are on the same WiFi network
- [ ] SensorServer app is installed and running on smartphone
- [ ] Smartphone IP address is configured in `imu_publisher.py`

---

## Starting the System

### 1. Start SensorServer on Smartphone

1. Open **SensorServer** app
2. Note the IP address displayed
3. Tap **Start Server**

### 2. Launch PocketFlight

**Gazebo Simulation:**

```bash
source ~/catkin_ws/devel/setup.bash
roslaunch pocketflight_imu start.launch
```

**DJI Tello (Real Hardware):**

```bash
source ~/catkin_ws/devel/setup.bash
roslaunch pocketflight_imu tello_control.launch
```

The system will:
1. Start IMU publisher node (connects to phone via WebSocket)
2. Start controller node
3. Automatically take off to 2.0 meters altitude

Wait for: `"Takeoff complete. Reached 2.0 meters."`

---

## Flight Controls

| Phone Motion | Drone Response |
|--------------|----------------|
| Tilt forward (pitch down) | Fly forward |
| Tilt backward (pitch up) | Fly backward |
| Tilt left (roll left) | Fly left |
| Tilt right (roll right) | Fly right |
| Rotate clockwise (yaw) | Rotate CW |
| Rotate counterclockwise | Rotate CCW |
| Hold level | Hover in place |

Altitude is automatically maintained by the PID controller.

---

## Monitoring

### Terminal Output

```
[controller] IMU Control | Side: 0.5, Forward: 1.2, Yaw: 0.0, Up: 0.0
```

### ROS Topics

```bash
# IMU data
rostopic echo /phone_imu_acc
rostopic echo /phone_imu_gyro

# Drone commands
rostopic echo /drone01/cmd_vel

# Topic rates
rostopic hz /phone_imu_acc
```

### Data Visualization

```bash
rosrun pocketflight_imu data_visualizer.py
```

Displays real-time plots of accelerometer, gyroscope, and velocity commands.

---

## Tuning

| Parameter | Default | Effect of Increasing |
|-----------|---------|---------------------|
| `SPEED_SCALING_FACTOR` | 1.0 | Faster drone response |
| `FILTER_ALPHA` | 0.2 | Less smoothing (more responsive, more jittery) |
| `DEADBAND_THRESHOLD` | 0.2 | Larger dead zone (less drift, less sensitivity) |
| `ALTITUDE_KP` | 0.5 | Faster altitude correction |
| `ALTITUDE_KI` | 0.1 | Eliminates steady-state altitude error |
| `ALTITUDE_KD` | 0.05 | Dampens altitude oscillation |

Edit these in `src/controller.py` or `config/imu_control.yaml`.

**Too sensitive?** Decrease `SPEED_SCALING_FACTOR`, decrease `FILTER_ALPHA`.
**Too sluggish?** Increase `SPEED_SCALING_FACTOR`, increase `FILTER_ALPHA`.
**Drifting when level?** Increase `DEADBAND_THRESHOLD`.

---

## Stopping the System

1. Press **Ctrl+C** in the launch terminal
2. Wait for all nodes to shut down
3. Stop SensorServer on smartphone

---

## Tips

- Start with small, gentle tilts to get familiar with response
- Hold the phone firmly with two hands
- Practice in Gazebo simulation before flying real hardware
- Keep phone roughly level; the system is most responsive to 10-30 degree tilts

---

## Next Steps

- See [Architecture](architecture.md) for system internals
- See [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute
