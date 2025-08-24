#!/usr/bin/python3

from os.path import join
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration,PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch.actions import AppendEnvironmentVariable, SetEnvironmentVariable
from pathlib import Path

def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time", default=True)

    bringup_path = get_package_share_directory("krobot_amr_bringup")
    urdf_path = get_package_share_directory("krobot_amr_description")
    world_file = LaunchConfiguration("world_file", default = join(bringup_path, "worlds", "maze.sdf"))
    gz_sim_share = get_package_share_directory("ros_gz_sim")

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(join(gz_sim_share, "launch", "gz_sim.launch.py")),
        launch_arguments={
            "gz_args" : PythonExpression(["'", world_file, " -r'"])

        }.items()
    )

    spawn_krobot_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(join(bringup_path, "launch", "spawn_krobot.launch.py")),
        launch_arguments={
            # Pass any arguments if your spawn.launch.py requires
        }.items()
    )

    return LaunchDescription([

        SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=[
            join(bringup_path, 'worlds'), ':' +
            join(bringup_path, 'models'), ':' +
            str(Path(urdf_path).parent.resolve())]),

        DeclareLaunchArgument("use_sim_time", default_value=use_sim_time),
        DeclareLaunchArgument("world_file", default_value=world_file),
        
        gz_sim, spawn_krobot_node
    ])