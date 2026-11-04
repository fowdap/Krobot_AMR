from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import os

def generate_launch_description():
    pkg_krobot_amr_navigation = get_package_share_directory('krobot_amr_navigation')

    # Path to your navigation parameters
    nav2_yaml = os.path.join(pkg_krobot_amr_navigation, 'config', 'navigation.yaml')

    # Nodes for the Nav2 stack
    controller_server_node = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[nav2_yaml]
    )

    nav2_smoother_node = Node(
        package='nav2_smoother',
        executable='smoother_server',
        name='smoother_server',
        output='screen',
        parameters=[nav2_yaml]
    )

    planner_server_node = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[nav2_yaml]
    )

    behavior_server_node = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[nav2_yaml]
    )

    nav2_bt_navigator_node = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[nav2_yaml]
    )

    nav2_waypoint_follower_node = Node(
        package='nav2_waypoint_follower',
        executable='waypoint_follower',
        name='waypoint_follower',
        output='screen',
        parameters=[nav2_yaml]
    )

    nav2_velocity_smoother_node = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        output='screen',
        parameters=[nav2_yaml]
    )

    # Lifecycle manager
    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [
                'controller_server',
                'smoother_server',
                'planner_server',
                'behavior_server',
                'bt_navigator',
                'waypoint_follower',
                'velocity_smoother',
            ]
        }]
    )

    return LaunchDescription([
        controller_server_node,
        nav2_smoother_node,
        planner_server_node,
        behavior_server_node,
        nav2_bt_navigator_node,
        nav2_waypoint_follower_node,
        nav2_velocity_smoother_node,
        lifecycle_manager_node
    ])
