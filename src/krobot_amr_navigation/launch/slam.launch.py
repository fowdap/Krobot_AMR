from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os
from launch_ros.actions import PushRosNamespace


ARGUMENTS = [
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='Use sim time'),
    DeclareLaunchArgument('namespace', default_value='',
                          description='Robot namespace')
]

def generate_launch_description():
    pkg_krobot_amr_navigation = get_package_share_directory('krobot_amr_navigation')
    

    slam_params_arg = DeclareLaunchArgument(
        'slam_params_file',
        default_value=os.path.join(pkg_krobot_amr_navigation, 'config', 'slam.yaml'),
        description='parameters file to use for the slam_toolbox node' )
    
    slam_params_file = LaunchConfiguration('slam_params_file')
    namespace = LaunchConfiguration('namespace')
    use_sim_time = LaunchConfiguration('use_sim_time')
    
    
    slam_node = GroupAction([
        PushRosNamespace(namespace),       
        Node(
            package='slam_toolbox',
            executable='sync_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                slam_params_file,
                {'use_sim_time': use_sim_time}
            ],
            
        )
    ])
    
    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(slam_params_arg)
    ld.add_action(slam_node)
    return ld
