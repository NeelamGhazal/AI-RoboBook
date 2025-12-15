#!/usr/bin/env python3
"""
Robot Spawning Script for RoboBook Module 2

This script demonstrates programmatic robot spawning in Gazebo using ROS 2 services.

Features:
- Spawn robots at specified positions
- Load robot model from URDF or SDF file
- Set initial pose (position and orientation)
- Handle multiple robots with unique names

Usage:
    python3 spawn_robot.py

Requirements:
    - ROS 2 Humble
    - Gazebo running with ros_tcp_endpoint
    - Robot model file (URDF or SDF)

Author: RoboBook Team
License: MIT
"""

import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity, DeleteEntity
from geometry_msgs.msg import Pose, Quaternion
import os
import sys


class RobotSpawner(Node):
    """
    Node for spawning and managing robots in Gazebo simulation.
    """

    def __init__(self):
        super().__init__('robot_spawner')

        # Create service clients
        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')
        self.delete_client = self.create_client(DeleteEntity, '/delete_entity')

        # Wait for services
        self.get_logger().info('Waiting for Gazebo services...')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Spawn service not available, waiting...')

        self.get_logger().info('Gazebo services ready!')

    def load_robot_description(self, file_path):
        """
        Load robot description from URDF or SDF file.

        Args:
            file_path (str): Path to robot description file

        Returns:
            str: Robot description XML
        """
        try:
            with open(file_path, 'r') as f:
                robot_xml = f.read()
            self.get_logger().info(f'Loaded robot description from {file_path}')
            return robot_xml
        except FileNotFoundError:
            self.get_logger().error(f'Robot description file not found: {file_path}')
            return None
        except Exception as e:
            self.get_logger().error(f'Error loading robot description: {str(e)}')
            return None

    def spawn_robot(self, robot_name, robot_xml, x=0.0, y=0.0, z=0.1,
                    roll=0.0, pitch=0.0, yaw=0.0, reference_frame='world'):
        """
        Spawn a robot in Gazebo at specified pose.

        Args:
            robot_name (str): Unique name for the robot instance
            robot_xml (str): Robot description (URDF or SDF)
            x, y, z (float): Position coordinates
            roll, pitch, yaw (float): Orientation in radians
            reference_frame (str): Reference frame for spawning

        Returns:
            bool: True if spawn successful, False otherwise
        """
        # Create spawn request
        request = SpawnEntity.Request()
        request.name = robot_name
        request.xml = robot_xml
        request.robot_namespace = robot_name
        request.reference_frame = reference_frame

        # Set initial pose
        request.initial_pose = Pose()
        request.initial_pose.position.x = x
        request.initial_pose.position.y = y
        request.initial_pose.position.z = z

        # Convert RPY to quaternion (simplified for small angles)
        request.initial_pose.orientation = self.euler_to_quaternion(roll, pitch, yaw)

        # Call spawn service
        self.get_logger().info(
            f'Spawning robot "{robot_name}" at position ({x:.2f}, {y:.2f}, {z:.2f})'
        )

        future = self.spawn_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            response = future.result()
            if response.success:
                self.get_logger().info(f'Successfully spawned robot "{robot_name}"')
                return True
            else:
                self.get_logger().error(
                    f'Failed to spawn robot "{robot_name}": {response.status_message}'
                )
                return False
        else:
            self.get_logger().error(f'Service call failed for robot "{robot_name}"')
            return False

    def delete_robot(self, robot_name):
        """
        Delete a robot from Gazebo simulation.

        Args:
            robot_name (str): Name of robot to delete

        Returns:
            bool: True if deletion successful, False otherwise
        """
        request = DeleteEntity.Request()
        request.name = robot_name

        self.get_logger().info(f'Deleting robot "{robot_name}"...')

        future = self.delete_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            response = future.result()
            if response.success:
                self.get_logger().info(f'Successfully deleted robot "{robot_name}"')
                return True
            else:
                self.get_logger().error(
                    f'Failed to delete robot "{robot_name}": {response.status_message}'
                )
                return False
        else:
            self.get_logger().error(f'Service call failed for robot "{robot_name}"')
            return False

    @staticmethod
    def euler_to_quaternion(roll, pitch, yaw):
        """
        Convert Euler angles to quaternion.

        Args:
            roll, pitch, yaw (float): Euler angles in radians

        Returns:
            Quaternion: ROS Quaternion message
        """
        import math

        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        q = Quaternion()
        q.w = cr * cp * cy + sr * sp * sy
        q.x = sr * cp * cy - cr * sp * sy
        q.y = cr * sp * cy + sr * cp * sy
        q.z = cr * cp * sy - sr * sp * cy

        return q


def main(args=None):
    """
    Main function to demonstrate robot spawning.
    """
    rclpy.init(args=args)

    # Create spawner node
    spawner = RobotSpawner()

    # Example: Spawn a simple box robot
    # You can replace this with your own URDF/SDF file
    simple_robot_xml = """
    <?xml version="1.0"?>
    <sdf version="1.8">
      <model name="simple_robot">
        <pose>0 0 0 0 0 0</pose>
        <link name="base_link">
          <inertial>
            <mass>1.0</mass>
            <inertia>
              <ixx>0.083</ixx>
              <ixy>0</ixy>
              <ixz>0</ixz>
              <iyy>0.083</iyy>
              <iyz>0</iyz>
              <izz>0.083</izz>
            </inertia>
          </inertial>
          <collision name="collision">
            <geometry>
              <box>
                <size>0.5 0.5 0.5</size>
              </box>
            </geometry>
          </collision>
          <visual name="visual">
            <geometry>
              <box>
                <size>0.5 0.5 0.5</size>
              </box>
            </geometry>
            <material>
              <ambient>0.0 0.5 1.0 1</ambient>
              <diffuse>0.0 0.5 1.0 1</diffuse>
            </material>
          </visual>
        </link>
      </model>
    </sdf>
    """

    # Spawn single robot
    spawner.spawn_robot('robot_1', simple_robot_xml, x=0.0, y=0.0, z=0.5)

    # Optional: Spawn multiple robots
    # spawner.spawn_robot('robot_2', simple_robot_xml, x=2.0, y=0.0, z=0.5)
    # spawner.spawn_robot('robot_3', simple_robot_xml, x=-2.0, y=0.0, z=0.5)

    # Optional: Load from file
    # robot_file_path = 'path/to/your/robot.sdf'
    # if os.path.exists(robot_file_path):
    #     robot_xml = spawner.load_robot_description(robot_file_path)
    #     if robot_xml:
    #         spawner.spawn_robot('custom_robot', robot_xml, x=1.0, y=1.0, z=0.2)

    spawner.get_logger().info('Robot spawning complete!')

    # Cleanup
    spawner.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
