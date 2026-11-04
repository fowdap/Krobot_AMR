# Krobot AMR

A differential-drive autonomous mobile robot (AMR) simulated in **Gazebo Harmonic** with **ROS 2 Jazzy**.
It carries a 2D lidar, an IMU, an RGB camera and a depth camera, and supports SLAM mapping
(slam_toolbox), localization (AMCL) and autonomous navigation (Nav2).

Maintainer: Kishor Sapkota <kishorsapkota490@gmail.com>

## Packages

| Package | Contents |
|---|---|
| `krobot_amr_description` | Robot model (xacro), meshes, Gazebo plugins and sensors |
| `krobot_amr_bringup` | Gazebo launch files, worlds (`maze`, `small_warehouse`) and warehouse models |
| `krobot_amr_navigation` | SLAM, localization and Nav2 launch files, configs and saved maps |

## Requirements

- Ubuntu 24.04
- ROS 2 Jazzy (Gazebo Harmonic comes with the `ros_gz` packages)

```bash
sudo apt install ros-jazzy-ros-gz ros-jazzy-xacro ros-jazzy-robot-state-publisher ros-jazzy-slam-toolbox ros-jazzy-navigation2 ros-jazzy-teleop-twist-keyboard ros-jazzy-rviz2
```

## Build

```bash
cd ~/Krobot_AMR
source /opt/ros/jazzy/setup.bash
colcon build
```

Every new terminal needs the workspace sourced first:

```bash
source ~/Krobot_AMR/install/setup.bash
```

## 1. Run the simulation

Maze world (default):

```bash
ros2 launch krobot_amr_bringup gazebo_igni.launch.py
```

Warehouse world:

```bash
ros2 launch krobot_amr_bringup gazebo_igni.launch.py world_file:=$(ros2 pkg prefix krobot_amr_bringup)/share/krobot_amr_bringup/worlds/small_warehouse.sdf
```

This starts Gazebo, spawns the robot at (0, 0), and starts `robot_state_publisher` and the ROS–Gazebo bridge.

### Drive the robot

In a new terminal:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Keep that terminal focused: `i` forward, `,` backward, `j` / `l` turn, `k` stop.

### View the robot in RViz

```bash
rviz2 -d $(ros2 pkg prefix krobot_amr_bringup)/share/krobot_amr_bringup/rviz/rviz_config.rviz --ros-args -p use_sim_time:=true
```

Set **Fixed Frame** to `odom` to see the robot move, and use **Add → By topic** to add `/scan`,
`/rgb_image` or `/depth_image/points`.

## 2. Make a map (SLAM)

**Terminal 1** – simulation:

```bash
ros2 launch krobot_amr_bringup gazebo_igni.launch.py
```

**Terminal 2** – SLAM:

```bash
ros2 launch krobot_amr_navigation slam.launch.py
```

**Terminal 3** – RViz (this config already shows the map and the laser scan):

```bash
rviz2 -d $(ros2 pkg prefix krobot_amr_navigation)/share/krobot_amr_navigation/config/localization_rviz.rviz --ros-args -p use_sim_time:=true
```

**Terminal 4** – drive around slowly with the keyboard until the whole area is mapped:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## 3. Save the map

While SLAM is still running, save the map into the navigation package:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/Krobot_AMR/src/krobot_amr_navigation/map/my_map --ros-args -p use_sim_time:=true
```

This writes `my_map.pgm` (the image) and `my_map.yaml` (resolution and origin).
You can then stop SLAM (Ctrl+C). Run `colcon build` again if you want the map installed with the package.

## 4. Localization (AMCL)

Stop SLAM first: it and AMCL both publish the `map → odom` transform.

**Terminal 1** – simulation:

```bash
ros2 launch krobot_amr_bringup gazebo_igni.launch.py
```

**Terminal 2** – map server, AMCL and RViz, using the provided maze map:

```bash
ros2 launch krobot_amr_navigation localization.launch.py
```

Or with your own map:

```bash
ros2 launch krobot_amr_navigation localization.launch.py map:=$HOME/Krobot_AMR/src/krobot_amr_navigation/map/my_map.yaml
```

The launch file publishes an initial pose at (0, 0), where the robot spawns. If the robot starts
somewhere else, or the laser scan doesn't line up with the map, click **2D Pose Estimate** in RViz
and drag from the robot's real position in the direction it faces.

Launch arguments: `map:=<path to yaml>` (default: `maze_map.yaml`), `rviz:=false` to start without RViz.

## 5. Navigation (Nav2)

Keep the simulation and localization running, then in **Terminal 3**:

```bash
ros2 launch krobot_amr_navigation navigation.launch.py
```

Wait for `Managed nodes are active` in the output. Then, in RViz, click **2D Goal Pose** and
click-drag on the map where the robot should go. Nav2 plans a path and drives the robot there,
avoiding obstacles seen by the lidar.

To send a goal from the command line:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: map}, pose: {position: {x: 1.5, y: 0.0}, orientation: {w: 1.0}}}}"
```

### Full navigation, in order

| Terminal | Command |
|---|---|
| 1 | `ros2 launch krobot_amr_bringup gazebo_igni.launch.py` |
| 2 | `ros2 launch krobot_amr_navigation localization.launch.py` |
| 3 | `ros2 launch krobot_amr_navigation navigation.launch.py` |

## Topics

| Topic | Type | Rate |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | input |
| `/scan` | `sensor_msgs/LaserScan` | 10 Hz |
| `/wheel_odom` | `nav_msgs/Odometry` | 20 Hz |
| `/imu` | `sensor_msgs/Imu` | 100 Hz |
| `/rgb_image`, `/rgb_camera/camera_info` | `sensor_msgs/Image`, `CameraInfo` | 30 Hz |
| `/depth_image`, `/depth_image/points` | `sensor_msgs/Image`, `PointCloud2` | 30 Hz |
| `/krobot/joint_states` | `sensor_msgs/JointState` | — |
| `/tf`, `/tf_static`, `/clock` | | — |

TF tree: `map → odom → base_footprint → base_link → sensors`. Gazebo's diff-drive plugin
publishes `odom → base_footprint`, and SLAM or AMCL publishes `map → odom`.

## Troubleshooting

- **Robot model shows red / "No transform" in RViz:** start RViz with `--ros-args -p use_sim_time:=true`.
- **"Detected jump back in time" or a robot that jumps around:** an old Gazebo is still running. Stop it with `pkill -f "gz sim"` and launch again.
- **Nav2 hangs at "Configuring ..." and never prints `Managed nodes are active`:** a service reply was occasionally lost in DDS. Stop navigation (Ctrl+C) and start it again.
- **Sensor rates lower than listed:** check the real-time factor in the bottom-right of Gazebo. Rates scale with it.
- **Gazebo warnings about `gz_frame_id`, `camera_info_topic` or `<static>`:** harmless; the sim works normally.
