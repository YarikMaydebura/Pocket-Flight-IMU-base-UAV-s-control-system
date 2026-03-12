#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import time

# Data storage for plotting
imu_acc_data = {"x": [], "y": [], "z": []}
imu_gyro_data = {"x": [], "y": [], "z": []}
cmd_vel_data = {"linear_x": [], "linear_y": [], "linear_z": [], "angular_z": []}
time_data = {"imu": [], "cmd_vel": []}

# Callback for IMU accelerometer data
def imu_acc_callback(msg):
    imu_acc_data["x"].append(msg.linear_acceleration.x)
    imu_acc_data["y"].append(msg.linear_acceleration.y)
    imu_acc_data["z"].append(msg.linear_acceleration.z)
    time_data["imu"].append(time.time())  # Use real-time timestamps

    # Limit stored data to the last 100 points
    if len(time_data["imu"]) > 100:
        for key in imu_acc_data:
            imu_acc_data[key] = imu_acc_data[key][-100:]
        time_data["imu"] = time_data["imu"][-100:]

# Callback for IMU gyroscope data
def imu_gyro_callback(msg):
    imu_gyro_data["x"].append(msg.angular_velocity.x)
    imu_gyro_data["y"].append(msg.angular_velocity.y)
    imu_gyro_data["z"].append(msg.angular_velocity.z)

    # Limit stored data to the last 100 points
    if len(imu_gyro_data["x"]) > 100:
        for key in imu_gyro_data:
            imu_gyro_data[key] = imu_gyro_data[key][-100:]

# Callback for cmd_vel data
def cmd_vel_callback(msg):
    cmd_vel_data["linear_x"].append(msg.linear.x)
    cmd_vel_data["linear_y"].append(msg.linear.y)
    cmd_vel_data["linear_z"].append(msg.linear.z)
    cmd_vel_data["angular_z"].append(msg.angular.z)
    time_data["cmd_vel"].append(time.time())  # Use real-time timestamps

    # Limit stored data to the last 100 points
    if len(cmd_vel_data["linear_x"]) > 100:
        for key in cmd_vel_data:
            cmd_vel_data[key] = cmd_vel_data[key][-100:]
        time_data["cmd_vel"] = time_data["cmd_vel"][-100:]

# ROS Subscriber Node
def ros_listener():
    rospy.Subscriber("/phone_imu_acc", Imu, imu_acc_callback)
    rospy.Subscriber("/phone_imu_gyro", Imu, imu_gyro_callback)
    rospy.Subscriber("/drone01/cmd_vel", Twist, cmd_vel_callback)
    rospy.spin()

# Real-time Plotting
def plot_data():
    fig, axs = plt.subplots(3, 1, figsize=(10, 8))

    # Animating function
    def update(frame):
        axs[0].clear()
        axs[1].clear()
        axs[2].clear()

        # Plot IMU accelerometer data
        if time_data["imu"]:
            axs[0].plot(time_data["imu"], imu_acc_data["x"], label="Acc X")
            axs[0].plot(time_data["imu"], imu_acc_data["y"], label="Acc Y")
            axs[0].plot(time_data["imu"], imu_acc_data["z"], label="Acc Z")
            axs[0].set_title("IMU Accelerometer")
            axs[0].legend()
            axs[0].grid()

        # Plot IMU gyroscope data
        if time_data["imu"]:
            axs[1].plot(time_data["imu"], imu_gyro_data["x"], label="Gyro X")
            axs[1].plot(time_data["imu"], imu_gyro_data["y"], label="Gyro Y")
            axs[1].plot(time_data["imu"], imu_gyro_data["z"], label="Gyro Z")
            axs[1].set_title("IMU Gyroscope")
            axs[1].legend()
            axs[1].grid()

        # Plot cmd_vel data
        if time_data["cmd_vel"]:
            axs[2].plot(time_data["cmd_vel"], cmd_vel_data["linear_x"], label="Linear X")
            axs[2].plot(time_data["cmd_vel"], cmd_vel_data["linear_y"], label="Linear Y")
            axs[2].plot(time_data["cmd_vel"], cmd_vel_data["linear_z"], label="Linear Z")
            axs[2].plot(time_data["cmd_vel"], cmd_vel_data["angular_z"], label="Angular Z")
            axs[2].set_title("Command Velocity (cmd_vel)")
            axs[2].legend()
            axs[2].grid()

        plt.tight_layout()

    ani = FuncAnimation(fig, update, interval=500)
    plt.show()

# Run ROS listener and plotting in separate threads
if __name__ == "__main__":
    # Initialize ROS in the main thread
    rospy.init_node("data_visualizer", anonymous=False)

    # Run the ROS listener in a separate thread
    listener_thread = threading.Thread(target=ros_listener)
    listener_thread.start()

    # Start plotting
    plot_data()
