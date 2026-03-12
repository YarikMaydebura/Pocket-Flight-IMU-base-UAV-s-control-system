cmake_minimum_required(VERSION 3.0.2)
project(pocketflight_imu)

find_package(catkin REQUIRED COMPONENTS
  rospy
  geometry_msgs
  sensor_msgs
  std_msgs
)

catkin_package()

# Install Python scripts
catkin_install_python(PROGRAMS
  src/imu_publisher.py
  src/controller.py
  src/tello_controller.py
  src/hector_control.py
  src/data_visualizer.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

# Install launch files
install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)

# Install config files
install(DIRECTORY config/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/config
)
