# realsense_gazebo_description

Check also the ROS1 branch for other info on that readme

## Instruction
To be used with https://github.com/ADVRHumanoids/realsense_gazebo_plugin, picking the correct ROS2 branch

## Info
ROS2 version of the realsense cameras (models). Taken copying and modifing:
- official realsense repo (https://github.com/IntelRealSense/realsense-ros/tree/ros2-master/realsense2_description), which does not include the "plugin tag" in the xacro for gazebo
- pal fork of the official realsense repo, which includes the "plugin tag" (but not the gazebo macro) https://github.com/pal-robotics-forks/realsense/tree/alum-devel/realsense2_description
- pal repo for realsense macro for gazebo, https://github.com/pal-robotics/realsense_simulation/tree/alum-devel. 

**Note** Recently https://github.com/pal-robotics/realsense_simulation/tree/alum-devel is marked as deprecated, in favour of https://github.com/pal-robotics/pal_urdf_utils. This one does not use anymore the custom PAL plugin for simulating the camera in gazebo, but the standard official ROS2: gazebo_ros_camera. Should we use this as well?

**Note2** Valerio work alternative? of this package: https://github.com/ADVRHumanoids/Depth_d435_ROS2_Gazebo_Ign