#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Imu
from std_msgs.msg import Float64MultiArray

# Constants
TAKEOFF_ALTITUDE = 3.0  # Target altitude for takeoff in meters
SPEED_SCALING_FACTOR = 5.0
TAKEOFF_SPEED = 1.0  # Speed of ascent during takeoff

class HectorQuadrotorController:
    def __init__(self):
        rospy.init_node('hector_quadrotor_controller', anonymous=True)
        
        # Command publisher for drone
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        # Initialize IMU data and altitude status
        self.imu_data_acc = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.imu_data_gyro = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.current_altitude = 0.0  # Track the drone's altitude
        self.reached_takeoff_altitude = False  # Takeoff status flag

        # Subscribe to the phone's IMU data topics
        rospy.Subscriber('/phone_imu_acc', Imu, self.imu_acc_callback)
        rospy.Subscriber('/phone_imu_gyro', Imu, self.imu_gyro_callback)

    def imu_acc_callback(self, msg):
        # Update accelerometer data from the callback
        self.imu_data_acc['x'] = msg.linear_acceleration.x
        self.imu_data_acc['y'] = msg.linear_acceleration.y
        self.imu_data_acc['z'] = msg.linear_acceleration.z

        # Estimate altitude based on IMU z-acceleration
        self.current_altitude += self.imu_data_acc['z'] * 0.1  # Simplified integration

    def imu_gyro_callback(self, msg):
        # Update gyroscope data from the callback
        self.imu_data_gyro['z'] = msg.angular_velocity.z

    def run(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            cmd_msg = Twist()

            # Check if drone has reached the takeoff altitude
            if not self.reached_takeoff_altitude:
                if self.current_altitude < TAKEOFF_ALTITUDE:
                    cmd_msg.linear.z = TAKEOFF_SPEED  # Ascend to target altitude
                    rospy.loginfo(f"Taking off | Current Altitude: {self.current_altitude:.2f}")
                else:
                    # Switch to IMU-based control after reaching takeoff altitude
                    self.reached_takeoff_altitude = True
                    rospy.loginfo("Takeoff complete. Switching to IMU-based control.")
            else:
                # IMU-based control once takeoff is complete
                roll = self.imu_data_acc['x']
                pitch = self.imu_data_acc['y']
                yaw_rate = self.imu_data_gyro['z']

                # Calculate control commands based on IMU input
                cmd_msg.linear.x = pitch
                cmd_msg.linear.y = roll
                cmd_msg.linear.z = 0  # Maintain current altitude
                cmd_msg.angular.z = yaw_rate

                rospy.loginfo(f"IMU Control | Roll: {roll}, Pitch: {pitch}, Yaw Rate: {yaw_rate}")

            # Publish command
            self.cmd_pub.publish(cmd_msg)
            rate.sleep()

if __name__ == "__main__":
    try:
        controller = HectorQuadrotorController()
        controller.run()
    except rospy.ROSInterruptException:
        pass
