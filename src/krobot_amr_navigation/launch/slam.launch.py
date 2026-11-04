from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, RegisterEventHandler
from launch.events import matches_action
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition
import os


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


    # slam_toolbox is a lifecycle node on Jazzy: it must be configured and
    # activated before it publishes /map and the map->odom transform.
    slam_node = LifecycleNode(
        package='slam_toolbox',
        executable='sync_slam_toolbox_node',
        name='slam_toolbox',
        namespace=namespace,
        output='screen',
        parameters=[
            slam_params_file,
            {'use_sim_time': use_sim_time}
        ],
    )

    configure_event = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(slam_node),
            transition_id=Transition.TRANSITION_CONFIGURE
        )
    )

    activate_event = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=slam_node,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                EmitEvent(event=ChangeState(
                    lifecycle_node_matcher=matches_action(slam_node),
                    transition_id=Transition.TRANSITION_ACTIVATE
                ))
            ]
        )
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(slam_params_arg)
    ld.add_action(slam_node)
    ld.add_action(configure_event)
    ld.add_action(activate_event)
    return ld
