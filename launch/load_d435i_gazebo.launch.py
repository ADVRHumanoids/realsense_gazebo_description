# Copyright 2023 Intel Corporation. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# /* Author: Doron Hirshberg */
import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
    IncludeLaunchDescription
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

from ament_index_python.packages import get_package_share_directory
import xacro

def launch_setup(context, *args, **kwargs):

    nodes_to_start = []

    rviz_config_dir = os.path.join(get_package_share_directory('realsense_gazebo_description'), 'rviz', 'd435i.rviz')
    xacro_file = os.path.join(get_package_share_directory('realsense_gazebo_description'), 'urdf', 'd435i_standalone.urdf.xacro')
    robot_description_content = xacro.process(
        xacro_file, 
        mappings={
            'use_nominal_extrinsics': 'true', 
            'add_plug': 'false',
            'use_mesh': 'true',
            'name': LaunchConfiguration("name").perform(context),
            'parent': LaunchConfiguration("parent").perform(context), 
            'x': LaunchConfiguration("pose_x").perform(context), 
            'y': LaunchConfiguration("pose_y").perform(context), 
            'z': LaunchConfiguration("pose_z").perform(context), 
            'roll': LaunchConfiguration("pose_roll").perform(context), 
            'yaw': LaunchConfiguration("pose_yaw").perform(context), 
            'pitch': LaunchConfiguration("pose_pitch").perform(context), 
            'publish_pointcloud': LaunchConfiguration("publish_pointcloud").perform(context), 
            'align_depth': LaunchConfiguration("align_depth").perform(context),
            'gazebo_urdf': LaunchConfiguration("gazebo_urdf").perform(context),
            'infra_enable': LaunchConfiguration("infra_enable").perform(context),
        },
    )
    urdf = {"robot_description": robot_description_content}

    nodes_to_start.append(Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        condition=IfCondition(LaunchConfiguration("rviz")),
        arguments=['-d', rviz_config_dir],
        parameters=[{
            'use_sim_time': (LaunchConfiguration("use_sim_time").perform(context) == True)
        }]
    ))
    nodes_to_start.append(Node(
        name='realsense_rsp',
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=LaunchConfiguration("name").perform(context),
        output='screen',
        condition=IfCondition(LaunchConfiguration("robot_state_publisher").perform(context)),
        parameters=[urdf, {
            "use_sim_time": (LaunchConfiguration("use_sim_time").perform(context) == True),
        }],
    ))

    ignition_simulator_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare("ros_gz_sim"), "/launch/gz_sim.launch.py"
        ], ),
        launch_arguments={
            "gz_args": f" -r -v 1 {LaunchConfiguration('world_file').perform(context)}",
        }.items(),
    )

    nodes_to_start.append(Node (
        name='urdf_spawner',
        package='ros_gz_sim',
        executable='create',
        namespace=LaunchConfiguration("name").perform(context),
        output='screen',
        arguments=[
            "-name", LaunchConfiguration("name").perform(context),
            #not sure why this must be doubled but it is like this the topic
            "-topic", "robot_description",
            # "-x", LaunchConfiguration('spawn_x').perform(context),
            # "-y", LaunchConfiguration('spawn_y').perform(context),
            # "-z", LaunchConfiguration('spawn_z').perform(context),
            # "-R", LaunchConfiguration('spawn_roll').perform(context),
            # "-P", LaunchConfiguration('spawn_pitch').perform(context),
            # "-Y", LaunchConfiguration('spawn_yaw').perform(context),
        ],
    ))

    # Gz sim bridge to ROS2
    if (LaunchConfiguration("align_depth").perform(context).lower() == "true"):
        bridge_topics = [
            # RGB Image topic is bridged with ros_gz_image
            f'/{LaunchConfiguration("name").perform(context)}/color/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            f'/{LaunchConfiguration("name").perform(context)}/aligned_depth_to_color/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            f'/{LaunchConfiguration("name").perform(context)}/aligned_depth_to_color/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            f'/{LaunchConfiguration("name").perform(context)}/aligned_depth_to_color/image_raw/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
        ]
        remappings = [
            (f'/{LaunchConfiguration("name").perform(context)}/aligned_depth_to_color/image_raw/points', 
                f'/{LaunchConfiguration("name").perform(context)}/aligned_depth_to_color/points')]
    else:
        bridge_topics = [
            # RGB Image topic is bridged with ros_gz_image
            f'/{LaunchConfiguration("name").perform(context)}/color/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            f'/{LaunchConfiguration("name").perform(context)}/depth/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            f'/{LaunchConfiguration("name").perform(context)}/depth/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            f'/{LaunchConfiguration("name").perform(context)}/depth/image_raw/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
        ]
        remappings = [
            (f'/{LaunchConfiguration("name").perform(context)}/depth/image_raw/points', 
                f'/{LaunchConfiguration("name").perform(context)}/depth/points')]
        
    # Infrared bridging
    if (LaunchConfiguration("infra_enable").perform(context).lower() == "true"):
        bridge_topics.extend([
            f'/{LaunchConfiguration("name").perform(context)}/infra1/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            f'/{LaunchConfiguration("name").perform(context)}/infra1/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
            f'/{LaunchConfiguration("name").perform(context)}/infra2/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            f'/{LaunchConfiguration("name").perform(context)}/infra2/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo',
        ])

    # RGB image uses ros_gz_image bridge and can be remapped per camera name.
    nodes_to_start.append(
        Node(
            package='ros_gz_image',
            executable='image_bridge',
            name=f'{LaunchConfiguration("name").perform(context)}_color_bridge',
            arguments=[f'/{LaunchConfiguration("name").perform(context)}/color/image_raw'],
        )
    )

    nodes_to_start.append(
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='ros_gz_bridge',
            arguments=bridge_topics,
            remappings=remappings,
        )
    )


    return [ignition_simulator_node] + nodes_to_start

def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(DeclareLaunchArgument("name", default_value="D435i_camera"))
    declared_arguments.append(DeclareLaunchArgument("parent", default_value="world"))
    declared_arguments.append(DeclareLaunchArgument("use_sim_time", default_value="true"))
    declared_arguments.append(DeclareLaunchArgument("rviz", default_value="false"))
    declared_arguments.append(DeclareLaunchArgument("robot_state_publisher", default_value="true"))
    declared_arguments.append(DeclareLaunchArgument("use_sim_time", default_value="true"))

    declared_arguments.append(DeclareLaunchArgument("pose_x", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("pose_y", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("pose_z", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("pose_roll", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("pose_pitch", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("pose_yaw", default_value="0.0"))

    declared_arguments.append(DeclareLaunchArgument("world_file", default_value =
        get_package_share_directory("realsense_gazebo_description") + "/worlds/empty.sdf"))
    # declared_arguments.append(DeclareLaunchArgument("spawn_x", default_value="0.0"))
    # declared_arguments.append(DeclareLaunchArgument("spawn_y", default_value="0.0"))
    # declared_arguments.append(DeclareLaunchArgument("spawn_z", default_value="0.2"))
    # declared_arguments.append(DeclareLaunchArgument("spawn_roll", default_value="0.0"))
    # declared_arguments.append(DeclareLaunchArgument("spawn_pitch", default_value="0.0"))
    # declared_arguments.append(DeclareLaunchArgument("spawn_yaw", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("publish_pointcloud", default_value="false"))
    declared_arguments.append(DeclareLaunchArgument("align_depth", default_value="false"))
    declared_arguments.append(DeclareLaunchArgument("gazebo_urdf", default_value="true"))
    declared_arguments.append(DeclareLaunchArgument("infra_enable", default_value="false"))


    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
