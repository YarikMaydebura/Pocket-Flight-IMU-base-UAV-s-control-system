#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu

# Constants
TAKEOFF_ALTITUDE = 2.0  # Target altitude in meters
MINIMUM_ALTITUDE = 1.0  # Minimum allowable altitude in meters
SPEED_SCALING_FACTOR = 0.2  # Scaling for IMU-based control
FILTER_ALPHA = 0.2  # Smoothing factor for low-pass filter
DEADBAND_THRESHOLD = 0.2  # Ignore small IMU z-axis values
GRAVITY = 9.81  # Gravity constant in m/s²

class TelloController:
    def __init__(self):
        rospy.init_node('tello_controller', anonymous=False)
        self.cmd_pub = rospy.Publisher('/tello/cmd_vel', Twist, queue_size=10)

        # Altitude and IMU data
        self.desired_altitude = TAKEOFF_ALTITUDE
        self.current_altitude = 0.0
        self.imu_data_acc = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.filtered_imu = {"x": 0.0, "y": 0.0, "z": 0.0}

        # IMU subscribers
        rospy.Subscriber('/phone_imu_acc', Imu, self.imu_acc_callback)

    def imu_acc_callback(self, msg):
        # Subtract gravity from the z-axis reading
        self.imu_data_acc["x"] = msg.linear_acceleration.x
        self.imu_data_acc["y"] = msg.linear_acceleration.y
        self.imu_data_acc["z"] = msg.linear_acceleration.z - GRAVITY

    def low_pass_filter(self, current_value, previous_value, alpha):
        """Applies a low-pass filter to smooth the input."""
        return alpha * current_value + (1 - alpha) * previous_value

    def run(self):
        """Handles IMU-based control."""
        rate = rospy.Rate(10)  # Run at 10 Hz

        while not rospy.is_shutdown():
            cmd_msg = Twist()

            # Smooth IMU input using a low-pass filter
            self.filtered_imu["x"] = self.low_pass_filter(
                self.imu_data_acc["x"], self.filtered_imu["x"], FILTER_ALPHA
            )
            self.filtered_imu["y"] = self.low_pass_filter(
                self.imu_data_acc["y"], self.filtered_imu["y"], FILTER_ALPHA
            )
            self.filtered_imu["z"] = self.low_pass_filter(
                self.imu_data_acc["z"], self.filtered_imu["z"], FILTER_ALPHA
            )

            # Adjust altitude based on filtered IMU z-axis
            if abs(self.filtered_imu["z"]) > DEADBAND_THRESHOLD:
                self.desired_altitude += self.filtered_imu["z"] * 0.1
                rospy.loginfo(f"Adjusted Desired Altitude: {self.desired_altitude}")

            # Enforce minimum altitude constraint
            if self.desired_altitude < MINIMUM_ALTITUDE:
                self.desired_altitude = MINIMUM_ALTITUDE

            # Set velocity commands
            cmd_msg.linear.z = (self.desired_altitude - self.current_altitude) * SPEED_SCALING_FACTOR
            cmd_msg.linear.x = self.filtered_imu["x"] * SPEED_SCALING_FACTOR
            cmd_msg.linear.y = self.filtered_imu["y"] * SPEED_SCALING_FACTOR
            cmd_msg.angular.z = 0.0  # Placeholder for yaw control

            rospy.loginfo(f"Command: {cmd_msg}")

            # Publish velocity command
            self.cmd_pub.publish(cmd_msg)
            rate.sleep()

if __name__ == "__main__":
    try:
        controller = TelloController()
        controller.run()
    except rospy.ROSInterruptException:
        pass
