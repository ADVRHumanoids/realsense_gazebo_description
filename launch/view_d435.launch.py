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
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import launch.events
from ament_index_python.packages import get_package_share_directory
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from launch_utils import to_urdf


def generate_launch_description():

    use_sim_time_arg = DeclareLaunchArgument("use_sim_time", default_value="true")
    rviz_arg = DeclareLaunchArgument("rviz", default_value="false")
    rsp_arg = DeclareLaunchArgument("robot_state_publisher", default_value="true")
    pub_world_tf_arg = DeclareLaunchArgument("pub_world_tf", default_value="false")

    pose_x_arg = DeclareLaunchArgument("pose_x", default_value="0.0")
    pose_y_arg = DeclareLaunchArgument("pose_y", default_value="0.0")
    pose_z_arg = DeclareLaunchArgument("pose_z", default_value="0.0")
    pose_roll_arg = DeclareLaunchArgument("pose_roll", default_value="0.0")
    pose_pitch_arg = DeclareLaunchArgument("pose_pitch", default_value="0.0")
    pose_yaw_arg = DeclareLaunchArgument("pose_yaw", default_value="0.0")

    rviz_config_dir = os.path.join(get_package_share_directory('realsense_gazebo_description'), 'rviz', 'd435i.rviz')
    xacro_path = os.path.join(get_package_share_directory('realsense_gazebo_description'), 'urdf', 'd435_standalone.urdf.xacro')
    urdf = to_urdf(xacro_path, {
        'use_nominal_extrinsics': 'true', 
        'add_plug': 'false',
        'name': 'D435_camera',

    })

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        condition=IfCondition(LaunchConfiguration("rviz")),
        arguments=['-d', rviz_config_dir],
        parameters=[{'use_sim_time': LaunchConfiguration("use_sim_time")}]
    )
    robot_state_publisher = Node(
        name='realsense_robot_state_publisher',
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace='d435',
        output='screen',
        condition=IfCondition(LaunchConfiguration("robot_state_publisher")),
        arguments=[urdf]
    )
    world_tf_pub = Node (
        name='realsense_world_tf_pub',
        package='tf2_ros',
        executable='static_transform_publisher',
        namespace='',
        output='screen',
        condition=IfCondition(LaunchConfiguration("pub_world_tf")),
        arguments=[
            "--frame-id", "world",
            "--child-frame-id", "D435_camera_bottom_screw_frame",
            "--x", LaunchConfiguration("pose_x"),
            "--y", LaunchConfiguration("pose_y"),
            "--z", LaunchConfiguration("pose_z"),
            "--roll", LaunchConfiguration("pose_roll"),
            "--pitch", LaunchConfiguration("pose_pitch"),
            "--yaw", LaunchConfiguration("pose_yaw"),

        ],
    )

    return LaunchDescription([
        use_sim_time_arg,
        rviz_arg,
        rsp_arg,
        pub_world_tf_arg,
        pose_x_arg,
        pose_y_arg,
        pose_z_arg,
        pose_roll_arg,
        pose_pitch_arg,
        pose_yaw_arg,
        rviz_node, 
        robot_state_publisher,
        world_tf_pub
    ])
