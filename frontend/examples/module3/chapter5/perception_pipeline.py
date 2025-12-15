#!/usr/bin/env python3
"""
Autonomous Navigation Script using BasicNavigator API

This script demonstrates waypoint navigation using Nav2's BasicNavigator
interface integrated with Isaac ROS Visual SLAM.

Usage:
    python3 perception_pipeline.py

Requirements:
    - Nav2 navigation stack running
    - Isaac ROS Visual SLAM running
    - Robot localized in map frame

Author: RoboBook Team
License: MIT
"""

import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped
import tf_transformations
import time


def create_pose_stamped(navigator, position_x, position_y, orientation_z):
    """
    Create a PoseStamped message with given position and orientation.

    Args:
        navigator: BasicNavigator instance
        position_x (float): X coordinate in map frame (meters)
        position_y (float): Y coordinate in map frame (meters)
        orientation_z (float): Yaw angle in radians

    Returns:
        PoseStamped: Pose message ready for navigation
    """
    # Convert yaw angle to quaternion
    q_x, q_y, q_z, q_w = tf_transformations.quaternion_from_euler(0.0, 0.0, orientation_z)

    # Create PoseStamped message
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()

    # Set position
    pose.pose.position.x = position_x
    pose.pose.position.y = position_y
    pose.pose.position.z = 0.0

    # Set orientation
    pose.pose.orientation.x = q_x
    pose.pose.orientation.y = q_y
    pose.pose.orientation.z = q_z
    pose.pose.orientation.w = q_w

    return pose


def navigate_waypoints(navigator, waypoints):
    """
    Navigate through a list of waypoints.

    Args:
        navigator: BasicNavigator instance
        waypoints: List of PoseStamped waypoints
    """
    print(f"Starting navigation through {len(waypoints)} waypoints...")

    # Start navigation
    navigator.followWaypoints(waypoints)

    # Monitor progress
    i = 0
    while not navigator.isTaskComplete():
        # Get feedback
        feedback = navigator.getFeedback()
        if feedback and i % 10 == 0:
            current = feedback.current_waypoint + 1
            total = len(waypoints)
            print(f'Progress: Waypoint {current}/{total}')
            print(f'Distance remaining: {feedback.distance_remaining:.2f}m')

        # Allow task to progress
        time.sleep(0.1)
        i += 1

    # Get final result
    result = navigator.getResult()

    if result == BasicNavigator.TaskResult.SUCCEEDED:
        print('✓ Navigation succeeded! All waypoints reached.')
        return True
    elif result == BasicNavigator.TaskResult.CANCELED:
        print('⚠ Navigation was canceled.')
        return False
    elif result == BasicNavigator.TaskResult.FAILED:
        print('✗ Navigation failed!')
        return False


def main():
    """
    Main navigation function demonstrating warehouse navigation.
    """
    print("=" * 60)
    print("RoboBook Module 3 - Perception Pipeline Demo")
    print("=" * 60)

    # Initialize ROS 2
    rclpy.init()

    # Create navigator
    navigator = BasicNavigator()

    print("\nWaiting for Nav2 to become active...")
    navigator.waitUntilNav2Active()
    print("✓ Nav2 is active and ready for navigation!")

    # Define warehouse waypoints (adjust for your environment)
    # Format: (x, y, yaw)
    waypoint_coords = [
        (3.5, 1.0, 0.0),      # Waypoint 1: Near entrance
        (5.5, 1.5, 1.57),     # Waypoint 2: Turn right
        (5.5, 4.5, 3.14),     # Waypoint 3: Far corner
        (2.0, 4.0, -1.57),    # Waypoint 4: Turn left
        (0.0, 0.0, 0.0),      # Waypoint 5: Return to start
    ]

    # Convert to PoseStamped messages
    waypoints = [
        create_pose_stamped(navigator, x, y, yaw)
        for x, y, yaw in waypoint_coords
    ]

    print(f"\nConfigured {len(waypoints)} waypoints:")
    for i, (x, y, yaw) in enumerate(waypoint_coords, 1):
        print(f"  {i}. Position: ({x:.1f}, {y:.1f}), Orientation: {yaw:.2f} rad")

    # Navigate through waypoints
    print("\n" + "-" * 60)
    print("Starting autonomous navigation...")
    print("-" * 60 + "\n")

    success = navigate_waypoints(navigator, waypoints)

    # Cleanup
    navigator.lifecycleShutdown()
    rclpy.shutdown()

    print("\n" + "=" * 60)
    if success:
        print("Demo completed successfully!")
    else:
        print("Demo ended with issues.")
    print("=" * 60)

    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
