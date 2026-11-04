from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
import os
from launch_ros.actions import PushRosNamespace
from launch_ros.actions import Node

ARGUMENTS = [
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='Use sim time'),
    DeclareLaunchArgument('namespace', default_value='',
                          description='Robot namespace')
]

def generate_launch_description():
    pkg_krobot_amr_navigation = get_package_share_directory('krobot_amr_navigation')

    rviz_config_path = os.path.join(get_package_share_directory('krobot_amr_navigation'),
                             'config','localization_rviz.rviz')
    

    nav2_yaml = os.path.join(pkg_krobot_amr_navigation, 'config', 'localization.yaml')
    map_file = os.path.join(pkg_krobot_amr_navigation, 'map', 'maze_map.yaml')

 
    rviz2_node = Node(
        package="rviz2",
        executable="rviz2",
        arguments=['-d', rviz_config_path]
    )

    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'use_sim_time': True}, 
                    {'yaml_filename': map_file}],
    )
            
    nav2_amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[nav2_yaml]
    )

    nav2_lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{'use_sim_time': True},
                    {'autostart': True},
                    {'node_names': ['map_server', 'amcl']}]
    )

    initial_pose_node = Node(
    package='krobot_amr_navigation',
    executable='initial_pose_pub.py',
    name='initial_pose_publisher',
    output='screen'
)



    return LaunchDescription([
        rviz2_node,
        map_server_node,
        nav2_amcl_node,
        nav2_lifecycle_manager_node,
        initial_pose_node

    ])
