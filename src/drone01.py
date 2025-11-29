#!/usr/bin/env python3
'''
@version: 4.0
@author: Shaiful Nizam
@since: May 23, 2022
@organization: RoboLab (Ritsumeikan University, College of Information Science and Engineering)
@note: This version will use 16 drones.
'''

import rospy
import os 
import math
import numpy as np
import configparser
import sys
import tempfile
import csv
import message_filters
import cv2, cv_bridge
from std_msgs.msg import Float64MultiArray, String, Int32, Float32MultiArray
from gazebo_msgs.msg import ModelStates
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import Image, CameraInfo, CompressedImage

drone_name = 'drone01'
targets = []

config = configparser.ConfigParser()
config.read('config.ini')

class Follower:
    def __init__(self):
        
        self.bridge = cv_bridge.CvBridge()
        rospy.Subscriber(drone_name+'/downward_cam/camera/image', Image, self.image_callback)
        rospy.Subscriber("controller", Float64MultiArray, self.pos_callback)
        rospy.Subscriber('/gazebo/model_states', ModelStates, self.callback)
        self.status = rospy.Publisher(drone_name+'/flood_status', Int32, queue_size = 10)
        self.moments = rospy.Publisher(drone_name+'/moments', Float32MultiArray, queue_size = 10)
        self.cmd_vel_pub = rospy.Publisher(drone_name+'/drone01/cmd_vel',Twist, queue_size=10)
        self.twist = Twist()
        self.file_counter = 1  # Counter for naming of saved image file.
        self.frame_counter = 5
     
    def pos_callback(self, data):
        global targets
        targets = np.array(data.data)
        targets = targets.reshape([-1,2])
        
    def image_callback(self, msg):

        # Get image from drone camera.        
        image = self.bridge.imgmsg_to_cv2(msg,desired_encoding='bgr8')
        # Slicing the image to remove vertical red lines
        image = image[:, 30:image.shape[1]-30, :] 
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE) # Rotate image clockwise by 90deg
        
        # Scale for resize.
        scale = float(config['down_scale']['scale'])
        
        # New dimensions for image.
        width = int(image.shape[1] * scale)
        height = int(image.shape[0] * scale)
        new_dimension = (width, height)
        
        # Syntax: cv2.resize([image source], [desired dimension], [interpolation])
        image = cv2.resize(image, new_dimension, cv2.INTER_AREA)  

        # Convert BGR to HSV color format.
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        #IMPORTANT NOTE: Color is in HSV format
        lower_boundary = np.array([int(config['color_range']['lower_H']),
                                   int(config['color_range']['lower_S']),
                                   int(config['color_range']['lower_V'])])
        upper_boundary = np.array([int(config['color_range']['upper_H']),
                                   int(config['color_range']['upper_S']),
                                   int(config['color_range']['upper_V'])])
        # print("["+drone_name+"] Lower boundary:", lower_boundary)
        # print("["+drone_name+"] Upper boundary:", upper_boundary)
        
        # cv2.inRange is used to render an image in white and black.
        # All the pixels that fall inside the interval [lower, upper] will be white
        # All the pixels that do not fall inside the interval will black, for all three channels:
        mask_flood = cv2.inRange(hsv_image, lower_boundary, upper_boundary)
        
        # All the pixels that are white in the mask will survive the AND operation, 
        # all the black pixels will remain black
        masked_image = cv2.bitwise_and(image, image, mask=mask_flood)

        # calculate moments of binary image
        M = cv2.moments(masked_image[:, :, 0].copy()) #make a copy with 1 channel to compute moments
        # Publish the required moments to ROS Topic
        moments = [M["m00"],M["m10"],M["m01"],M["m11"],M["m20"],M["m02"]]
        print("["+drone_name+"] moments:", moments)
        self.moments.publish(Float32MultiArray(data = moments))

        # Use the mask to count the number of white pixels.
        # Number of white pixels divide by the image size to get the ratio.
        flood_percent = (cv2.countNonZero(mask_flood) / (hsv_image.shape[0]*hsv_image.shape[1])) * 100
        print("["+drone_name+"] Flood percentage:", np.round(flood_percent, 2))        

        # Flood detection logic
        flood_threshold = float(config['flood_threshold']['value'])
        print("["+drone_name+"] Flood threshold:", flood_threshold)
        if flood_percent < flood_threshold:
            state = 0
            print("["+drone_name+"] No flood detected.")
        elif flood_percent >= flood_threshold:
            state = 1
            print("["+drone_name+"] Flood detected.")
        else:
            state = 0 # Default state when no condition is satisfied.
            print("["+drone_name+"] Initializing...")
            
        self.status.publish(state) # Send state to ROS publisher.
            
        # cv2.imshow(drone_name, image)
        
        #===========================================================================================================
        # Save image to file. PLEASE COMMENT OUT WHEN NOT NEEDED.
        #===========================================================================================================
        # if (self.frame_counter == 5):
        #     if self.file_counter < 10:
        #         cv2.imwrite('images/' + drone_name + '/FIG_000' + str(self.file_counter) + '.png', np.hstack([image, masked_image]))
        #     elif self.file_counter >= 10 and self.file_counter < 100:
        #         cv2.imwrite('images/' + drone_name + '/FIG_00' + str(self.file_counter) + '.png', np.hstack([image, masked_image]))
        #     elif self.file_counter >= 100 and self.file_counter < 1000:
        #         cv2.imwrite('images/' + drone_name + '/FIG_0' + str(self.file_counter) + '.png', np.hstack([image, masked_image]))
        #     else:
        #         cv2.imwrite('images/' + drone_name + '/FIG_' + str(self.file_counter) + '.png', np.hstack([image, masked_image]))
        #     self.frame_counter = 0            
        #     self.file_counter += 1
        # self.frame_counter += 1
        #===========================================================================================================

        # Display drone camera image and masked image
        cv2.imshow(drone_name, np.hstack([image, masked_image]))
        cv2.waitKey(3)
        
    def callback(self, data):
        drone = data.pose[int(config['g_index'][drone_name])]
        posX = drone.position.x
        posY = drone.position.y
        posZ = drone.position.z
        
        global targets
        if len(targets) != 0:
            targetZ = float(config['position']['ceiling_height'])
            v_vel_scale = float(config['velocity']['v_vel_scale'])       # The velocity in the vertical plane
            if posZ < (targetZ - 1):
                # Move the drone straight up vertically when drone is not yet at ceiling height.
                calc_odom = (Vector3(0, 0, v_vel_scale*(posZ-targetZ)))
            else:
                # When drone is at ceiling height then move it to target.
                target = targets[int(config['index'][drone_name])]
                targetX = target[0]
                targetY = target[1]
                h_vel_scale = float(config['velocity']['h_vel_scale'])       # The velocity in the horizontal plane
                calc_odom = (Vector3(h_vel_scale * (posX-targetX), h_vel_scale * (posY-targetY), v_vel_scale*(posZ-targetZ)))
            pub = self.cmd_vel_pub
            pub.publish(Twist(calc_odom, Vector3(0,0,0)))
            
        rospy.Rate(10).sleep
    
def listener():
    rospy.init_node(drone_name)
    follower = Follower()
    rospy.spin()

if __name__ == '__main__':
    try:
        listener()
    except rospy.ROSInterruptException:
        pass
# END ALL
