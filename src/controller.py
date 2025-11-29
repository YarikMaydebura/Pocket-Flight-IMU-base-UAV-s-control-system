#!/usr/bin/env python3

import rospy
import time
from gazebo_msgs.srv import GetModelState, GetModelStateRequest
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu

# Constants
TAKEOFF_ALTITUDE = 2.0  # Target altitude in meters
MINIMUM_ALTITUDE = 1.0  # Minimum allowable altitude in meters
TAKEOFF_SPEED = 0.5  # Speed of ascent
SPEED_SCALING_FACTOR = 1.0  # Scaling for IMU-based control
ALTITUDE_TOLERANCE = 0.05  # Allowable error in meters
FILTER_ALPHA = 0.2  # Smoothing factor for low-pass filter
GRAVITY = 9.81  # Gravity constant in m/s²
DEADBAND_THRESHOLD = 0.2  # Ignore small IMU z-axis values
ALTITUDE_KP = 0.5  # Proportional gain for altitude control
ALTITUDE_KI = 0.1  # Integral gain for altitude control
ALTITUDE_KD = 0.05  # Derivative gain for altitude control

# Only one drone for this IMU-based control system
drone_name = 'drone01'

# Helper to get the drone's position
def get_pose(drone_name):
    try:
        sets = GetModelStateRequest()
        sets.model_name = drone_name
        response = service_call(sets)
        return response.pose
    except rospy.ServiceException as e:
        rospy.logerr(f"Failed to get drone pose: {e}")
        return None

class HectorQuadrotorController:
    def __init__(self):
        rospy.init_node('drone01_controller', anonymous=False)
        self.cmd_pub = rospy.Publisher('/drone01/cmd_vel', Twist, queue_size=10)

        # Altitude and IMU data
        self.current_altitude = 0.0
        self.desired_altitude = TAKEOFF_ALTITUDE
        self.imu_data_acc = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.imu_data_gyro = {"z": 0.0}

        # PID controller variables
        self.altitude_error_sum = 0.0
        self.last_altitude_error = 0.0

        # Filtering values
        self.filtered_imu = {
            "linear_x": 0.0,
            "linear_y": 0.0,
            "linear_z": 0.0,
            "angular_z": 0.0,
        }

        # IMU subscribers
        rospy.Subscriber('/phone_imu_acc', Imu, self.imu_acc_callback)
        rospy.Subscriber('/phone_imu_gyro', Imu, self.imu_gyro_callback)

    def imu_acc_callback(self, msg):
        # Subtract gravity from the z-axis reading
        self.imu_data_acc["x"] = msg.linear_acceleration.x
        self.imu_data_acc["y"] = msg.linear_acceleration.y
        self.imu_data_acc["z"] = msg.linear_acceleration.z - GRAVITY

    def imu_gyro_callback(self, msg):
        self.imu_data_gyro["z"] = msg.angular_velocity.z

    def low_pass_filter(self, current_value, previous_value, alpha):
        """Applies a low-pass filter to smooth the input."""
        return alpha * current_value + (1 - alpha) * previous_value

    def enforce_minimum_altitude(self):
        """Ensure the drone does not go below the minimum altitude."""
        if self.desired_altitude < MINIMUM_ALTITUDE:
            rospy.logwarn(f"Desired altitude ({self.desired_altitude:.2f}m) below minimum. Adjusting to {MINIMUM_ALTITUDE}m.")
            self.desired_altitude = MINIMUM_ALTITUDE

    def takeoff(self):
        """Handles the drone's initial takeoff to a target altitude."""
        rospy.loginfo("Initiating takeoff sequence...")
        rate = rospy.Rate(10)  # Run at 10 Hz

        while not rospy.is_shutdown():
            pose = get_pose(drone_name)
            if pose is not None:
                self.current_altitude = pose.position.z
                altitude_error = TAKEOFF_ALTITUDE - self.current_altitude

                if abs(altitude_error) <= ALTITUDE_TOLERANCE:
                    rospy.loginfo(f"Takeoff complete. Reached {self.current_altitude} meters.")
                    return  # Exit the takeoff loop

                # Command to ascend
                cmd_msg = Twist()
                cmd_msg.linear.z = min(max(altitude_error * 0.5, -TAKEOFF_SPEED), TAKEOFF_SPEED)
                self.cmd_pub.publish(cmd_msg)
                rospy.loginfo(f"Taking off | Current Altitude: {self.current_altitude:.2f}, Altitude Error: {altitude_error:.2f}")

            rate.sleep()

    def pid_control_altitude(self):
        """PID control for altitude stabilization."""
        altitude_error = self.desired_altitude - self.current_altitude
        self.altitude_error_sum += altitude_error
        altitude_derivative = altitude_error - self.last_altitude_error
        self.last_altitude_error = altitude_error

        pid_output = (
            ALTITUDE_KP * altitude_error
            + ALTITUDE_KI * self.altitude_error_sum
            + ALTITUDE_KD * altitude_derivative
        )
        return pid_output

    def run(self):
        """Handles IMU-based control after takeoff."""
        rate = rospy.Rate(10)  # Run at 10 Hz

        while not rospy.is_shutdown():
            cmd_msg = Twist()
            pose = get_pose(drone_name)

            if pose is not None:
                self.current_altitude = pose.position.z
                rospy.loginfo(f"Current Altitude: {self.current_altitude}, Desired Altitude: {self.desired_altitude}")

            # Smooth IMU input using a low-pass filter
            self.filtered_imu["linear_x"] = self.low_pass_filter(
                self.imu_data_acc["x"], self.filtered_imu["linear_x"], FILTER_ALPHA
            )
            self.filtered_imu["linear_y"] = self.low_pass_filter(
                self.imu_data_acc["y"], self.filtered_imu["linear_y"], FILTER_ALPHA
            )
            self.filtered_imu["linear_z"] = self.low_pass_filter(
                self.imu_data_acc["z"], self.filtered_imu["linear_z"], FILTER_ALPHA
            )

            # Ignore small IMU z-axis changes (deadband)
            if abs(self.filtered_imu["linear_z"]) > DEADBAND_THRESHOLD:
                self.desired_altitude += self.filtered_imu["linear_z"] * 0.1
                rospy.loginfo(f"Adjusted Desired Altitude: {self.desired_altitude}")

            # Enforce minimum altitude constraint
            self.enforce_minimum_altitude()

            # PID control for altitude
            cmd_msg.linear.z = min(max(self.pid_control_altitude(), -1.0), 1.0)

            # Set filtered commands for linear.x, linear.y, and angular.z
            cmd_msg.linear.x = self.filtered_imu["linear_x"] * SPEED_SCALING_FACTOR
            cmd_msg.linear.y = self.filtered_imu["linear_y"] * SPEED_SCALING_FACTOR
            cmd_msg.angular.z = self.filtered_imu["angular_z"] * SPEED_SCALING_FACTOR

            rospy.loginfo(f"IMU Control | Side: {cmd_msg.linear.x}, Forward: {cmd_msg.linear.y}, Yaw: {cmd_msg.angular.z}, Up: {cmd_msg.linear.z}")

            # Publish the command
            self.cmd_pub.publish(cmd_msg)
            rate.sleep()


if __name__ == "__main__":
    try:
        rospy.wait_for_service('/gazebo/get_model_state')
        service_call = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
        controller = HectorQuadrotorController()
        controller.takeoff()  # Perform the takeoff sequence
        controller.run()  # Transition to IMU-based control
    except rospy.ROSInterruptException:
        pass
