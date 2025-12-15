---
sidebar_label: 'Chapter 5: Hands-on: Perception Pipeline'
sidebar_position: 5
---

# Chapter 5: Hands-on: Perception Pipeline ⏱️ 90 minutes

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Set up a complete Isaac Sim environment with a mobile robot
2. Configure and launch Isaac ROS Visual SLAM
3. Integrate VSLAM with Nav2 for autonomous navigation
4. Tune perception and navigation parameters
5. Test the complete pipeline in simulation
6. Troubleshoot common integration issues
7. Extend the pipeline for real robot deployment

---

## Prerequisites

Before starting this tutorial, ensure you have:

- ✅ Completed Module 3 Chapters 1-4
- ✅ Ubuntu 22.04 with ROS 2 Humble installed
- ✅ NVIDIA GPU (RTX 3060 or better) with drivers ≥525
- ✅ Isaac Sim 2023.1.1 installed
- ✅ Isaac ROS workspace set up
- ✅ 50GB free disk space
- ✅ Basic understanding of ROS 2 concepts

**Estimated Time**: 90 minutes

---

## Step 1: Environment Setup (10 minutes)

### 1.1 Create Project Workspace

```bash
# Create workspace
mkdir -p ~/perception_pipeline_ws/src
cd ~/perception_pipeline_ws/src

# Clone required packages
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git

# Clone Nav2
git clone -b humble https://github.com/ros-planning/navigation2.git

# Return to workspace root
cd ~/perception_pipeline_ws

# Install dependencies
rosdep install --from-paths src --ignore-src -r -y

# Build workspace
colcon build --symlink-install --packages-up-to \
    isaac_ros_visual_slam \
    nav2_bringup \
    nav2_simple_commander

# Source workspace
source install/setup.bash
```

### 1.2 Verify Installation

```bash
# Check Isaac ROS VSLAM
ros2 pkg list | grep isaac_ros_visual_slam

# Check Nav2
ros2 pkg list | grep nav2_bringup

# Expected output:
# isaac_ros_visual_slam
# nav2_bringup
# nav2_msgs
# ... (other Nav2 packages)
```

---

## Step 2: Create Isaac Sim Scene (15 minutes)

### 2.1 Scene Structure

Create `warehouse_scene.py`:

```python
"""
Isaac Sim warehouse scene with mobile robot.
"""

from isaacsim import SimulationApp

# Launch Isaac Sim
simulation_app = SimulationApp({"headless": False})

import omni
from omni.isaac.core import World
from omni.isaac.core.objects import GroundPlane, VisualCuboid
from omni.isaac.wheeled_robots.robots import WheeledRobot
from omni.isaac.wheeled_robots.controllers.differential_controller import DifferentialController
from omni.isaac.core.utils.types import ArticulationAction
from omni.isaac.sensor import Camera
from omni.isaac.range_sensor import LidarRtx
import numpy as np

# Create world
world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()

print("Creating warehouse environment...")

# Add warehouse walls
walls = [
    # North wall
    ("/World/wall_north", np.array([0, 10, 1.5]), np.array([20, 0.2, 3])),
    # South wall
    ("/World/wall_south", np.array([0, -10, 1.5]), np.array([20, 0.2, 3])),
    # East wall
    ("/World/wall_east", np.array([10, 0, 1.5]), np.array([0.2, 20, 3])),
    # West wall
    ("/World/wall_west", np.array([-10, 0, 1.5]), np.array([0.2, 20, 3])),
]

for wall_path, position, scale in walls:
    wall = world.scene.add(
        VisualCuboid(
            prim_path=wall_path,
            name=wall_path.split("/")[-1],
            position=position,
            scale=scale,
            color=np.array([0.7, 0.7, 0.7])
        )
    )

# Add obstacles (storage boxes)
obstacles = [
    ("/World/box_1", np.array([3, 3, 0.5]), np.array([1, 1, 1])),
    ("/World/box_2", np.array([-3, -3, 0.5]), np.array([1, 1, 1])),
    ("/World/box_3", np.array([-5, 5, 0.5]), np.array([1.2, 1.2, 1])),
    ("/World/box_4", np.array([6, -3, 0.6]), np.array([0.8, 0.8, 1.2])),
]

for box_path, position, scale in obstacles:
    box = world.scene.add(
        VisualCuboid(
            prim_path=box_path,
            name=box_path.split("/")[-1],
            position=position,
            scale=scale,
            color=np.array([0.8, 0.5, 0.2])
        )
    )

# Create mobile robot
print("Adding mobile robot...")
robot = world.scene.add(
    WheeledRobot(
        prim_path="/World/robot",
        name="mobile_robot",
        wheel_dof_names=["left_wheel_joint", "right_wheel_joint"],
        create_robot=True,
        position=np.array([0, 0, 0.1])
    )
)

# Add stereo cameras to robot
left_camera = Camera(
    prim_path="/World/robot/left_camera",
    frequency=30,
    resolution=(640, 480),
    position=np.array([0.2, 0.05, 0.3]),
    orientation=np.array([0, 0, 0, 1])
)

right_camera = Camera(
    prim_path="/World/robot/right_camera",
    frequency=30,
    resolution=(640, 480),
    position=np.array([0.2, -0.05, 0.3]),
    orientation=np.array([0, 0, 0, 1])
)

# Add LiDAR sensor
lidar = LidarRtx(
    prim_path="/World/robot/lidar",
    position=np.array([0.15, 0, 0.35]),
    orientation=np.array([0, 0, 0, 1]),
    config="OS1_64"  # Ouster OS1-64 config
)

# Initialize ROS 2 bridge
from omni.isaac.core.utils.extensions import enable_extension
enable_extension("omni.isaac.ros2_bridge")

print("Scene created successfully!")
print("Starting simulation...")

# Reset world
world.reset()

# Differential drive controller
controller = DifferentialController(name="simple_control", wheel_radius=0.05, wheel_base=0.3)

# Simulation loop
frame_count = 0
try:
    while simulation_app.is_running():
        world.step(render=True)

        # Simple forward motion for testing
        if frame_count < 1000:
            action = ArticulationAction(joint_velocities=[1.0, 1.0])
            robot.apply_action(action)

        frame_count += 1

        if frame_count % 100 == 0:
            print(f"Frame: {frame_count}")

except KeyboardInterrupt:
    print("Simulation stopped by user")

# Cleanup
simulation_app.close()
```

### 2.2 Launch Scene

```bash
# Launch Isaac Sim with warehouse scene
~/.local/share/ov/pkg/isaac_sim-2023.1.1/python.sh warehouse_scene.py

# Verify:
# - Robot appears at origin
# - Warehouse walls and boxes visible
# - Robot has cameras and LiDAR attached
```

---

## Step 3: Configure Isaac ROS VSLAM (15 minutes)

### 3.1 Create VSLAM Launch File

Create `isaac_vslam_launch.py`:

```python
"""
Isaac ROS Visual SLAM launch file for perception pipeline.
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    """Generate launch description."""

    # Arguments
    enable_imu_arg = DeclareLaunchArgument(
        'enable_imu',
        default_value='false'
    )

    # Isaac ROS Visual SLAM node
    visual_slam_node = Node(
        package='isaac_ros_visual_slam',
        executable='isaac_ros_visual_slam',
        name='visual_slam',
        output='screen',
        parameters=[{
            # Camera configuration
            'denoise_input_images': False,
            'rectified_images': True,
            'enable_debug_mode': True,
            'enable_slam_visualization': True,
            'enable_landmarks_view': True,
            'enable_observations_view': True,

            # SLAM parameters
            'num_cameras': 2,
            'min_num_images': 2,
            'max_frame_rate': 30.0,

            # Feature tracking
            'enable_localization_n_mapping': True,
            'enable_imu_fusion': LaunchConfiguration('enable_imu'),

            # Map parameters
            'map_frame': 'map',
            'odom_frame': 'odom',
            'base_frame': 'base_link',
            'camera_optical_frames': ['left_camera_optical', 'right_camera_optical'],

            # Performance
            'gpu_id': 0,
            'enable_verbosity': True,

            # Tuning parameters
            'num_features': 800,
            'feature_quality_threshold': 0.01,
            'min_parallax_deg': 1.0,
            'max_keyframes': 100,
        }],
        remappings=[
            ('stereo_camera/left/image', '/robot/left_camera/rgb'),
            ('stereo_camera/left/camera_info', '/robot/left_camera/camera_info'),
            ('stereo_camera/right/image', '/robot/right_camera/rgb'),
            ('stereo_camera/right/camera_info', '/robot/right_camera/camera_info'),
            ('visual_slam/tracking/odometry', '/odom'),
        ]
    )

    # Static TF publishers for camera extrinsics
    left_camera_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='left_camera_tf',
        arguments=['0.2', '0.05', '0.3', '0', '0', '0', 'base_link', 'left_camera_optical']
    )

    right_camera_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='right_camera_tf',
        arguments=['0.2', '-0.05', '0.3', '0', '0', '0', 'base_link', 'right_camera_optical']
    )

    return LaunchDescription([
        enable_imu_arg,
        visual_slam_node,
        left_camera_tf,
        right_camera_tf,
    ])
```

### 3.2 Test VSLAM

```bash
# Terminal 1: Launch Isaac Sim scene
python3 warehouse_scene.py

# Terminal 2: Launch Isaac ROS VSLAM
source ~/perception_pipeline_ws/install/setup.bash
ros2 launch perception_pipeline isaac_vslam_launch.py

# Terminal 3: Monitor VSLAM topics
ros2 topic list | grep visual_slam

# Expected topics:
# /visual_slam/status
# /visual_slam/tracking/odometry
# /visual_slam/tracking/slam_path
# /visual_slam/tracking/vo_pose

# Terminal 4: Visualize in RViz2
rviz2
# Add displays: TF, Odometry (/odom), Path (/visual_slam/tracking/slam_path)
```

---

## Step 4: Configure Nav2 (20 minutes)

### 4.1 Create Nav2 Parameter File

Create `nav2_params.yaml`:

```yaml
# Nav2 configuration for perception pipeline

bt_navigator:
  ros__parameters:
    use_sim_time: False
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    bt_loop_duration: 10
    default_server_timeout: 20
    enable_groot_monitoring: True
    groot_zmq_publisher_port: 1666
    groot_zmq_server_port: 1667
    plugin_lib_names:
    - nav2_compute_path_to_pose_action_bt_node
    - nav2_compute_path_through_poses_action_bt_node
    - nav2_smooth_path_action_bt_node
    - nav2_follow_path_action_bt_node
    - nav2_spin_action_bt_node
    - nav2_wait_action_bt_node
    - nav2_back_up_action_bt_node
    - nav2_drive_on_heading_bt_node
    - nav2_clear_costmap_service_bt_node
    - nav2_is_stuck_condition_bt_node
    - nav2_goal_reached_condition_bt_node
    - nav2_goal_updated_condition_bt_node
    - nav2_globally_updated_goal_condition_bt_node
    - nav2_is_path_valid_condition_bt_node
    - nav2_initial_pose_received_condition_bt_node
    - nav2_reinitialize_global_localization_service_bt_node
    - nav2_rate_controller_bt_node
    - nav2_distance_controller_bt_node
    - nav2_speed_controller_bt_node
    - nav2_truncate_path_action_bt_node
    - nav2_truncate_path_local_action_bt_node
    - nav2_goal_updater_node_bt_node
    - nav2_recovery_node_bt_node
    - nav2_pipeline_sequence_bt_node
    - nav2_round_robin_node_bt_node
    - nav2_transform_available_condition_bt_node
    - nav2_time_expired_condition_bt_node
    - nav2_path_expiring_timer_condition
    - nav2_distance_traveled_condition_bt_node
    - nav2_single_trigger_bt_node
    - nav2_goal_updated_controller_bt_node
    - nav2_is_battery_low_condition_bt_node
    - nav2_navigate_through_poses_action_bt_node
    - nav2_navigate_to_pose_action_bt_node
    - nav2_remove_passed_goals_action_bt_node
    - nav2_planner_selector_bt_node
    - nav2_controller_selector_bt_node
    - nav2_goal_checker_selector_bt_node
    - nav2_controller_cancel_bt_node
    - nav2_path_longer_on_approach_bt_node
    - nav2_wait_cancel_bt_node
    - nav2_spin_cancel_bt_node
    - nav2_back_up_cancel_bt_node
    - nav2_drive_on_heading_cancel_bt_node

controller_server:
  ros__parameters:
    use_sim_time: False
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    failure_tolerance: 0.3
    progress_checker_plugin: "progress_checker"
    goal_checker_plugins: ["general_goal_checker"]
    controller_plugins: ["FollowPath"]

    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0

    general_goal_checker:
      stateful: True
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.25
      yaw_goal_tolerance: 0.25

    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      min_vel_x: 0.0
      min_vel_y: 0.0
      max_vel_x: 0.4
      max_vel_y: 0.0
      max_vel_theta: 0.8
      min_speed_xy: 0.0
      max_speed_xy: 0.4
      min_speed_theta: 0.0
      acc_lim_x: 2.5
      acc_lim_y: 0.0
      acc_lim_theta: 3.2
      decel_lim_x: -2.5
      decel_lim_y: 0.0
      decel_lim_theta: -3.2
      vx_samples: 20
      vy_samples: 0
      vtheta_samples: 40
      sim_time: 1.7
      linear_granularity: 0.05
      angular_granularity: 0.025
      transform_tolerance: 0.2
      xy_goal_tolerance: 0.25
      trans_stopped_velocity: 0.25
      short_circuit_trajectory_evaluation: True
      stateful: True
      critics: ["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign", "PathAlign", "PathDist", "GoalDist"]
      BaseObstacle.scale: 0.02
      PathAlign.scale: 32.0
      PathAlign.forward_point_distance: 0.1
      GoalAlign.scale: 24.0
      GoalAlign.forward_point_distance: 0.1
      PathDist.scale: 32.0
      GoalDist.scale: 24.0
      RotateToGoal.scale: 32.0
      RotateToGoal.slowing_factor: 5.0
      RotateToGoal.lookahead_time: -1.0

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: False
      rolling_window: true
      width: 8
      height: 8
      resolution: 0.05
      robot_radius: 0.3
      plugins: ["voxel_layer", "inflation_layer"]
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55
      voxel_layer:
        plugin: "nav2_costmap_2d::VoxelLayer"
        enabled: True
        publish_voxel_map: True
        origin_z: 0.0
        z_resolution: 0.05
        z_voxels: 16
        max_obstacle_height: 2.0
        mark_threshold: 0
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: False
      robot_radius: 0.3
      resolution: 0.05
      track_unknown_space: true
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: True
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: True
          marking: True
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: True
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55

planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    use_sim_time: False
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_smac_planner/SmacPlanner2D"
      tolerance: 0.125
      downsample_costmap: false
      downsampling_factor: 1
      allow_unknown: true
      max_iterations: 1000000
      max_on_approach_iterations: 1000
      max_planning_time: 2.0
      motion_model_for_search: "MOORE"
      cost_travel_multiplier: 2.0
      use_final_approach_orientation: false
      smoother:
        max_iterations: 1000
        w_smooth: 0.3
        w_data: 0.2
        tolerance: 0.000001

recoveries_server:
  ros__parameters:
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/published_footprint
    cycle_frequency: 10.0
    recovery_plugins: ["spin", "backup", "wait"]
    spin:
      plugin: "nav2_recoveries::Spin"
    backup:
      plugin: "nav2_recoveries::BackUp"
    wait:
      plugin: "nav2_recoveries::Wait"
```

---

## Step 5: Integration Testing (20 minutes)

### 5.1 Create Master Launch File

Create `perception_pipeline_launch.py`:

```python
"""
Complete perception pipeline launch file.
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    """Generate complete pipeline launch description."""

    # Package directories
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    config_dir = os.path.join(os.getcwd(), 'config')

    # Launch Isaac ROS VSLAM
    vslam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(os.getcwd(), 'isaac_vslam_launch.py')
        )
    )

    # Launch Nav2
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'False',
            'params_file': os.path.join(config_dir, 'nav2_params.yaml')
        }.items()
    )

    return LaunchDescription([
        vslam_launch,
        nav2_launch,
    ])
```

### 5.2 Full System Test

```bash
# Terminal 1: Launch Isaac Sim
python3 warehouse_scene.py

# Terminal 2: Launch perception pipeline
source ~/perception_pipeline_ws/install/setup.bash
ros2 launch perception_pipeline perception_pipeline_launch.py

# Terminal 3: Launch RViz2
rviz2

# In RViz2:
# - Set Fixed Frame: map
# - Add: TF, Map, Local Costmap, Global Costmap, Path, Robot Model

# Terminal 4: Send navigation goal
ros2 topic pub --once /goal_pose geometry_msgs/PoseStamped "{
  header: {frame_id: 'map'},
  pose: {
    position: {x: 5.0, y: 5.0, z: 0.0},
    orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
  }
}"
```

---

## Step 6: Parameter Tuning (10 minutes)

### 6.1 VSLAM Tuning Checklist

| Parameter | Effect | Recommended Value |
|-----------|--------|-------------------|
| `num_features` | More features = better tracking | 600-1000 |
| `feature_quality_threshold` | Lower = more features | 0.005-0.02 |
| `min_parallax_deg` | Minimum motion for keyframe | 0.5-2.0° |
| `max_keyframes` | Memory usage | 50-150 |

### 6.2 Nav2 Tuning Checklist

| Parameter | Effect | Recommended Value |
|-----------|--------|-------------------|
| `max_vel_x` | Robot max speed | 0.3-0.5 m/s |
| `inflation_radius` | Safety margin | 1.5× robot radius |
| `vx_samples` | Velocity sampling | 15-25 |
| `sim_time` | Prediction horizon | 1.5-2.0 seconds |

---

## Step 7: Troubleshooting (5 minutes)

### Common Issues

**Issue 1: VSLAM Tracking Loss**
```bash
# Check feature count
ros2 topic echo /visual_slam/status

# Solution: Increase lighting or add textures to environment
```

**Issue 2: Nav2 Not Finding Path**
```bash
# Check costmap topics
ros2 topic echo /global_costmap/costmap

# Solution: Verify map frame is published, check inflation radius
```

**Issue 3: Robot Not Moving**
```bash
# Check cmd_vel commands
ros2 topic echo /cmd_vel

# Solution: Verify controller frequency, check motor limits
```

---

## Step 8: Extensions (5 minutes)

### 8.1 Add Object Detection

Integrate YOLO for object detection:

```python
# Add to scene
from omni.isaac.dnn_inference import TensorRTInference

detector = TensorRTInference(
    model_path="/models/yolov8n.onnx",
    input_topics=["/robot/left_camera/rgb"],
    output_topic="/detections"
)
```

### 8.2 Real Robot Deployment Checklist

- [ ] Replace Isaac Sim topics with real camera topics
- [ ] Calibrate cameras (intrinsics and extrinsics)
- [ ] Add IMU fusion for better odometry
- [ ] Tune parameters for real-world lighting
- [ ] Add safety limits (cliff detection, emergency stop)
- [ ] Test in controlled environment first
- [ ] Log all data for analysis

---

## Assessment Checklist

Complete the following to verify your pipeline:

- [ ] Isaac Sim scene loads with robot and sensors
- [ ] VSLAM publishes odometry at 30Hz
- [ ] TF tree shows map → odom → base_link chain
- [ ] Global costmap shows static obstacles (walls, boxes)
- [ ] Local costmap shows sensor data (LiDAR)
- [ ] Nav2 successfully plans path from start to goal
- [ ] Robot navigates autonomously avoiding obstacles
- [ ] Recovery behaviors work when robot gets stuck
- [ ] All nodes run without errors for 5+ minutes
- [ ] Documentation created for your specific setup

---

## Summary

In this hands-on tutorial, you:

- ✅ Set up a complete Isaac Sim warehouse environment
- ✅ Configured Isaac ROS Visual SLAM for localization
- ✅ Integrated VSLAM with Nav2 navigation stack
- ✅ Tuned perception and navigation parameters
- ✅ Tested autonomous navigation in simulation
- ✅ Learned troubleshooting techniques
- ✅ Prepared for real robot deployment

**Next Steps:**
- Deploy to real robot with RealSense/ZED camera
- Add multi-floor mapping with elevators
- Integrate object detection and manipulation
- Implement fleet management for multiple robots

---

**Congratulations!** You've built a complete perception and navigation pipeline integrating Isaac Sim, VSLAM, and Nav2. This forms the foundation for advanced autonomous robot applications.

**Module 3 Complete** - Proceed to Module 4 for voice control and LLM integration.
