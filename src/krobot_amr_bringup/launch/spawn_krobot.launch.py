#!/usr/bin/python3

from os.path import join
from xacro import parse, process_doc

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import AppendEnvironmentVariable

from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
   
    urdf_path = get_package_share_directory("krobot_amr_description")
    position_x = LaunchConfiguration("position_x")
    position_y = LaunchConfiguration("position_y")
    orientation_yaw = LaunchConfiguration("orientation_yaw")

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        parameters=[
                    {'robot_description': Command( \
                    ['xacro ', join(urdf_path, 'urdf/robot_urdf.urdf.xacro'),
                    ' sim_ign:=', "true", 
                    ])},
                    {'use_sim_time': True}],
        remappings=[
            ('/joint_states', 'krobot/joint_states'),
        ]
    )

    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "/robot_description",
            "-name", "krobot",
            "-allow_renaming", "true",
            "-z", "0.00368",
            "-x", position_x,
            "-y", position_y,
            "-Y", orientation_yaw
        ]
    )

    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist",
            "/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock",
            "/world/maze/model/krobot/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model",
            "/wheel_odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
            "/rgb_image@sensor_msgs/msg/Image[ignition.msgs.Image",
            "/depth_image@sensor_msgs/msg/Image[ignition.msgs.Image",
            "rgb_camera/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo",
            "/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan",
            "/depth_image/points@sensor_msgs/msg/PointCloud2[ignition.msgs.PointCloudPacked"
        ],
        remappings=[
            ('/world/maze/model/krobot/joint_state', 'krobot/joint_states'),

        ]
    )




    return LaunchDescription([

        # Add both model path and resource path
        AppendEnvironmentVariable(
        name='IGN_GAZEBO_MODEL_PATH',
        value=[get_package_share_directory("krobot_amr_description")]),

        AppendEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=[join(get_package_share_directory("krobot_amr_description"), "meshes")]),

        DeclareLaunchArgument("position_x", default_value="0.0"),
        DeclareLaunchArgument("position_y", default_value="0.0"),
        DeclareLaunchArgument("orientation_yaw", default_value="0.0"),
        DeclareLaunchArgument("odometry_source", default_value="world"),
        robot_state_publisher,
        gz_spawn_entity,
        gz_ros2_bridge,
    ])