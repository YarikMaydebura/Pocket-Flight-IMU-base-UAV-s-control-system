#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Imu
import websocket
import json
import threading

# Global variable to hold the IMU data for accelerometer and gyroscope
imu_data_acc = None
imu_data_gyro = None

# Enable WebSocket debug tracing
websocket.enableTrace(True)

def on_message_acc(ws, message):
    global imu_data_acc
    try:
        data = json.loads(message)
        imu_msg = Imu()

        # Parse accelerometer data
        if 'values' in data:
            imu_msg.linear_acceleration.x = data['values'][0]
            imu_msg.linear_acceleration.y = data['values'][1]
            imu_msg.linear_acceleration.z = data['values'][2]

        # Set timestamp (if available)
        imu_msg.header.stamp = rospy.Time.now()  # Using ROS time

        # Set default covariance values (can be tuned according to sensor specs)
        imu_msg.linear_acceleration_covariance = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        imu_msg.orientation_covariance = [-1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # No orientation data

        imu_data_acc = imu_msg
    except json.JSONDecodeError as e:
        rospy.logerr(f"Error decoding accelerometer message: {e}")
    except Exception as e:
        rospy.logerr(f"Error processing accelerometer message: {e}")

def on_message_gyro(ws, message):
    global imu_data_gyro
    try:
        data = json.loads(message)
        imu_msg = Imu()

        # Parse gyroscope data
        if 'values' in data:
            imu_msg.angular_velocity.x = data['values'][0]
            imu_msg.angular_velocity.y = data['values'][1]
            imu_msg.angular_velocity.z = data['values'][2]

        # Set timestamp (if available)
        imu_msg.header.stamp = rospy.Time.now()  # Using ROS time

        # Set default covariance values (can be tuned according to sensor specs)
        imu_msg.angular_velocity_covariance = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        imu_msg.orientation_covariance = [-1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # No orientation data

        imu_data_gyro = imu_msg
    except json.JSONDecodeError as e:
        rospy.logerr(f"Error decoding gyroscope message: {e}")
    except Exception as e:
        rospy.logerr(f"Error processing gyroscope message: {e}")

def on_error(ws, error):
    rospy.logerr(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    rospy.loginfo(f"WebSocket connection closed with code: {close_status_code}, message: {close_msg}")

def on_open(ws):
    rospy.loginfo("WebSocket connection established")

def imu_publisher():
    """ ROS node to publish IMU data. """
    global imu_data_acc, imu_data_gyro
    rospy.init_node('imu_publisher', anonymous=False)

    pub_acc = rospy.Publisher('/phone_imu_acc', Imu, queue_size=10)
    pub_gyro = rospy.Publisher('/phone_imu_gyro', Imu, queue_size=10)
    rate = rospy.Rate(20)

    while not rospy.is_shutdown():
        if imu_data_acc:
            pub_acc.publish(imu_data_acc)
        if imu_data_gyro:
            pub_gyro.publish(imu_data_gyro)
        rate.sleep()

if __name__ == '__main__':
    # WebSocket connections for accelerometer and gyroscope sensors
    ws_acc = websocket.WebSocketApp("ws://192.168.0.243:8080/sensor/connect?type=android.sensor.accelerometer",
                                    on_open=on_open,
                                    on_message=on_message_acc,
                                    on_error=on_error,
                                    on_close=on_close)

    ws_gyro = websocket.WebSocketApp("ws://192.168.0.243:8080/sensor/connect?type=android.sensor.gyroscope",
                                     on_open=on_open,
                                     on_message=on_message_gyro,
                                     on_error=on_error,
                                     on_close=on_close)

    # Start WebSocket connections in separate threads for both sensors
    threading.Thread(target=ws_acc.run_forever).start()
    threading.Thread(target=ws_gyro.run_forever).start()

    # Start ROS publisher
    try:
        imu_publisher()
    except rospy.ROSInterruptException:
        pass
