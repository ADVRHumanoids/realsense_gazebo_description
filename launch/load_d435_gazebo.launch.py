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
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import launch.events
from ament_index_python.packages import get_package_share_directory
import sys
import xacro

def launch_setup(context, *args, **kwargs):

    nodes_to_start = []

    rviz_config_dir = os.path.join(get_package_share_directory('realsense_gazebo_description'), 'rviz', 'd435.rviz')
    xacro_file = os.path.join(get_package_share_directory('realsense_gazebo_description'), 'urdf', 'd435_standalone.urdf.xacro')
    robot_description_content = xacro.process(
        xacro_file, 
        mappings={
            'use_nominal_extrinsics': 'true', 
            'add_plug': 'false',
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
    nodes_to_start.append(Node (
        name='realsense_world_tf_pub',
        package='tf2_ros',
        executable='static_transform_publisher',
        namespace='',
        output='screen',
        condition=IfCondition(LaunchConfiguration("pub_world_tf")),
        arguments=[
            "--frame-id", "world",
            "--child-frame-id", "D435_camera_bottom_screw_frame",
            "--x", LaunchConfiguration("pose_x").perform(context),
            "--y", LaunchConfiguration("pose_y").perform(context),
            "--z", LaunchConfiguration("pose_z").perform(context),
            "--roll", LaunchConfiguration("pose_roll").perform(context),
            "--pitch", LaunchConfiguration("pose_pitch").perform(context),
            "--yaw", LaunchConfiguration("pose_yaw").perform(context),

        ],
    ))

    ###
    ### SIMULATOR TODO
    ###
    # world_file = os.path.join(
    #     get_package_share_path("doosan_gazebo"), "world", "doosan.world"
    # )
    # ignition_simulator_node = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([
    #         FindPackageShare("ros_gz_sim"), "/launch/gz_sim.launch.py"
    #     ], ),
    #     launch_arguments={
    #         "gz_args": f" -r -v 1 {world_file}",
    #     }.items(),
    #     condition=IfCondition(simulator)
    # )

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
            "-x", LaunchConfiguration('spawn_x').perform(context),
            "-y", LaunchConfiguration('spawn_y').perform(context),
            "-z", LaunchConfiguration('spawn_z').perform(context),
            "-R", LaunchConfiguration('spawn_roll').perform(context),
            "-P", LaunchConfiguration('spawn_pitch').perform(context),
            "-Y", LaunchConfiguration('spawn_yaw').perform(context),
        ],
    ))

    return nodes_to_start

def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(DeclareLaunchArgument("name", default_value="D435_camera"))
    declared_arguments.append(DeclareLaunchArgument("parent", default_value="world"))
    declared_arguments.append(DeclareLaunchArgument("use_sim_time", default_value="true"))
    declared_arguments.append(DeclareLaunchArgument("rviz", default_value="false"))
    declared_arguments.append(DeclareLaunchArgument("robot_state_publisher", default_value="true"))
    declared_arguments.append(DeclareLaunchArgument("pub_world_tf", default_value="false"))
    declared_arguments.append(DeclareLaunchArgument("use_sim_time", default_value="true"))

    declared_arguments.append(DeclareLaunchArgument("pose_x", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("pose_y", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("pose_z", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("pose_roll", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("pose_pitch", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("pose_yaw", default_value="0.0"))

    declared_arguments.append(DeclareLaunchArgument("gazebo", default_value="false"))
    declared_arguments.append(DeclareLaunchArgument("spawn_x", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("spawn_y", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("spawn_z", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("spawn_roll", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("spawn_pitch", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("spawn_yaw", default_value="0.0"))
    declared_arguments.append(DeclareLaunchArgument("publish_pointcloud", default_value="false"))
    declared_arguments.append(DeclareLaunchArgument("align_depth", default_value="true"))



    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
