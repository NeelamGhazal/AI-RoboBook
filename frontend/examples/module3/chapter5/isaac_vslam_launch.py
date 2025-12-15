#!/usr/bin/env python3
"""
Isaac ROS Visual SLAM Launch File for RoboBook Module 3

This launch file starts the Isaac ROS Visual SLAM node configured for
the warehouse perception pipeline tutorial.

Usage:
    ros2 launch module3_examples isaac_vslam_launch.py

Requirements:
    - Isaac ROS Visual SLAM package installed
    - Stereo camera or RGB-D sensor
    - NVIDIA GPU with CUDA support

Author: RoboBook Team
License: MIT
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    """Generate launch description for Isaac ROS Visual SLAM."""

    # Declare launch arguments
    enable_imu_arg = DeclareLaunchArgument(
        'enable_imu',
        default_value='false',
        description='Enable IMU fusion for improved odometry'
    )

    enable_debug_arg = DeclareLaunchArgument(
        'enable_debug',
        default_value='true',
        description='Enable debug visualization'
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
            'enable_debug_mode': LaunchConfiguration('enable_debug'),
            'enable_slam_visualization': True,
            'enable_landmarks_view': True,
            'enable_observations_view': True,

            # SLAM parameters
            'num_cameras': 2,  # Stereo setup
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

            # Performance tuning
            'gpu_id': 0,
            'enable_verbosity': True,

            # Feature detection parameters
            'num_features': 800,
            'feature_quality_threshold': 0.01,
            'min_parallax_deg': 1.0,
            'max_keyframes': 100,

            # Loop closure
            'enable_loop_closure': True,
            'loop_closure_frequency': 1.0,
            'min_loop_closure_score': 0.5,
        }],
        remappings=[
            # Remap to your camera topics
            ('stereo_camera/left/image', '/robot/left_camera/rgb'),
            ('stereo_camera/left/camera_info', '/robot/left_camera/camera_info'),
            ('stereo_camera/right/image', '/robot/right_camera/rgb'),
            ('stereo_camera/right/camera_info', '/robot/right_camera/camera_info'),
            ('visual_slam/tracking/odometry', '/odom'),
        ]
    )

    # Static TF publishers for camera extrinsics
    # Adjust these values based on your robot's camera placement
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
        enable_debug_arg,
        visual_slam_node,
        left_camera_tf,
        right_camera_tf,
    ])
