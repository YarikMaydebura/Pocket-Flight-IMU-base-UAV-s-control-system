# Usage Guide

This guide explains how to use PocketFlight to control a drone with your smartphone.

## Table of Contents

1. [Pre-flight Checklist](#pre-flight-checklist)
2. [Starting the System](#starting-the-system)
3. [Flying the Drone](#flying-the-drone)
4. [Understanding Control Mappings](#understanding-control-mappings)
5. [Monitoring](#monitoring)
6. [Stopping the System](#stopping-the-system)
7. [Tips and Best Practices](#tips-and-best-practices)

---

## Pre-flight Checklist

Before starting, ensure:

- [ ] ROS Noetic is installed and sourced
- [ ] Catkin workspace is built and sourced
- [ ] Smartphone and PC are on the same WiFi network
- [ ] SensorServer app is installed on smartphone
- [ ] Smartphone IP address is configured in `imu_publisher.py`
- [ ] Gazebo is working properly

---

## Starting the System

### Step 1: Start SensorServer on Smartphone

1. Open **SensorServer** app on your phone
2. Note the IP address displayed (e.g., `192.168.1.100`)
3. Tap **Start Server** button
4. Keep the app in foreground or allow background running

### Step 2: Verify Network Connection

On your PC, test connectivity:

```bash
ping YOUR_PHONE_IP
```

If successful, you'll see responses. Press Ctrl+C to stop.

### Step 3: Source ROS Workspace

```bash
source ~/catkin_ws/devel/setup.bash
```

### Step 4: Launch PocketFlight

```bash
roslaunch flood_monitor_16 start.launch
```

### What Happens During Launch

The system will:
1. Start ROS core
2. Launch Gazebo simulation with flood environment
3. Spawn the drone (drone01)
4. Start IMU publisher node
5. Start controller node
6. Automatically take off to 2 meters altitude

**Wait for these messages:**
- "WebSocket connection established"
- "Takeoff complete. Reached 2.0 meters."

---

## Flying the Drone

### Basic Control

Once the drone has taken off, you can control it by moving your smartphone:

#### Forward/Backward Movement
- **Tilt phone forward** (pitch down) → Drone flies forward
- **Tilt phone backward** (pitch up) → Drone flies backward

#### Left/Right Movement
- **Tilt phone left** (roll left) → Drone flies left
- **Tilt phone right** (roll right) → Drone flies right

#### Rotation
- **Rotate phone clockwise** → Drone rotates clockwise
- **Rotate phone counterclockwise** → Drone rotates counterclockwise

#### Altitude Control
- Altitude is automatically maintained at takeoff level
- PID controller keeps drone stable at desired height

### Control Sensitivity

The system uses **low-pass filtering** for smooth control:
- Small movements are ignored (deadband threshold)
- Sudden jerks are smoothed out
- Response is proportional to tilt angle

### Holding Position

To make the drone hover in place:
- Hold your phone level (horizontal)
- Minimize rotation
- The drone will automatically stabilize

---

## Understanding Control Mappings

### IMU to Drone Velocity Mapping

| Phone Motion | IMU Reading | Drone Command |
|--------------|-------------|---------------|
| Forward tilt | +pitch | linear.x (forward) |
| Backward tilt | -pitch | linear.x (backward) |
| Left tilt | +roll | linear.y (left) |
| Right tilt | -roll | linear.y (right) |
| Clockwise rotation | +yaw | angular.z (CW) |
| CCW rotation | -yaw | angular.z (CCW) |

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `SPEED_SCALING_FACTOR` | 1.0 | Overall speed multiplier |
| `FILTER_ALPHA` | 0.2 | Smoothing (0=no filter, 1=no smoothing) |
| `DEADBAND_THRESHOLD` | 0.2 | Ignore movements below this |
| `TAKEOFF_ALTITUDE` | 2.0 m | Automatic takeoff height |

Edit these in `src/controller.py` to tune behavior.

---

## Monitoring

### Terminal Output

Monitor the system through terminal logs:

```bash
# In the launch terminal, you'll see:
[controller] IMU Control | Side: 0.5, Forward: 1.2, Yaw: 0.0, Up: 0.0
[drone01] Flood percentage: 25.3
[drone01] No flood detected.
```

### ROS Topics

Monitor topics in separate terminals:

**IMU Data:**
```bash
rostopic echo /phone_imu_acc
rostopic echo /phone_imu_gyro
```

**Drone Commands:**
```bash
rostopic echo /drone01/cmd_vel
```

**Drone Position:**
```bash
rostopic echo /gazebo/model_states
```

### Gazebo Visualization

In Gazebo window:
- Watch drone movement in real-time
- View camera feed (if enabled)
- Monitor flood detection visualization

---

## Stopping the System

### Graceful Shutdown

1. **Land the drone first** (optional manual landing)
2. Press **Ctrl+C** in the launch terminal
3. Wait for all nodes to shut down
4. Stop SensorServer on smartphone

### Emergency Stop

If needed:
- Press Ctrl+C immediately
- The drone will stop receiving commands and hover
- May descend slowly if in simulation

---

## Tips and Best Practices

### For Smooth Control

1. **Start with small movements**
   - Make gentle tilts initially
   - Get familiar with response

2. **Hold phone firmly**
   - Use two hands if needed
   - Avoid shaking

3. **Keep phone roughly level**
   - Don't tilt excessively
   - The system is most responsive to 10-30° tilts

4. **Practice in simulation first**
   - Master control in Gazebo before real hardware
   - Test different environments

### Tuning for Your Preference

**If drone is too sensitive:**
```python
# In controller.py
SPEED_SCALING_FACTOR = 0.5  # Reduce from 1.0
FILTER_ALPHA = 0.1          # More smoothing (reduce from 0.2)
```

**If drone is too slow:**
```python
SPEED_SCALING_FACTOR = 1.5  # Increase from 1.0
FILTER_ALPHA = 0.3          # Less smoothing (increase from 0.2)
```

**If drone drifts when phone is level:**
```python
DEADBAND_THRESHOLD = 0.3    # Increase from 0.2
```

### Troubleshooting During Flight

**Drone not responding:**
- Check IMU data is publishing: `rostopic hz /phone_imu_acc`
- Verify WebSocket connection
- Restart SensorServer app

**Jerky movements:**
- Increase `FILTER_ALPHA` for more smoothing
- Check network latency
- Ensure phone isn't running heavy background apps

**Drone drifting:**
- Calibrate phone sensors (in phone settings)
- Increase deadband threshold
- Check for IMU bias in readings

---

## Advanced Usage

### Multi-Drone Mode

To enable multiple drones (currently commented out in `flood_monitor.launch`):

1. Edit `launch/flood_monitor.launch`
2. Uncomment drone sections (drone02, drone03, etc.)
3. Each drone spawns at 3-second intervals

### Flood Monitoring Mode

The system includes flood detection:
- Camera analyzes ground color
- HSV color segmentation detects water
- Publishes flood status to `/drone01/flood_status`

Configure in `config/config.ini`:
```ini
[color_range]
lower_H = 95
upper_H = 104
# ... adjust for your flood color
```

### Custom Configurations

Edit `config/config.ini` for:
- Flight ceiling height
- Velocity scaling
- Flood detection thresholds
- Color ranges

---

## Example Flight Session

```bash
# Terminal 1: Launch system
source ~/catkin_ws/devel/setup.bash
roslaunch flood_monitor_16 start.launch

# Terminal 2: Monitor IMU (optional)
rostopic echo /phone_imu_acc

# Terminal 3: Monitor velocity commands (optional)
rostopic echo /drone01/cmd_vel

# On smartphone:
# - Open SensorServer
# - Start server
# - Begin flying by tilting phone

# When done:
# - Press Ctrl+C in Terminal 1
# - Stop SensorServer
```

---

## Next Steps

- Explore [Architecture Documentation](architecture.md) to understand system internals
- Modify parameters for your use case
- Contribute improvements (see [CONTRIBUTING.md](../CONTRIBUTING.md))

---

Happy Flying! 🚁
