#!/usr/bin/env python3
"""
Simple ROS 2 Publisher Example

This node publishes a "Hello World" message to a topic every 0.5 seconds.

MIT License
Copyright (c) 2025 RoboBook
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimplePublisher(Node):
    """
    A simple ROS 2 publisher node that sends messages to a topic.
    """

    def __init__(self):
        """
        Initialize the node with a name and create publisher.
        """
        super().__init__('simple_publisher')

        # Create a publisher for String messages on the 'chatter' topic
        self.publisher_ = self.create_publisher(String, 'chatter', 10)

        # Create a timer to publish messages every 0.5 seconds
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Counter for message numbering
        self.i = 0

        # Log that the publisher has started
        self.get_logger().info('Simple Publisher node initialized')

    def timer_callback(self):
        """
        Callback function that runs every timer tick.
        Creates and publishes a message.
        """
        # Create a String message
        msg = String()
        msg.data = f'Hello World: {self.i}'

        # Publish the message
        self.publisher_.publish(msg)

        # Log the published message
        self.get_logger().info(f'Publishing: "{msg.data}"')

        # Increment the counter
        self.i += 1


def main(args=None):
    """
    Main function to initialize and run the publisher node.
    """
    # Initialize ROS 2
    rclpy.init(args=args)

    # Create the publisher node
    simple_publisher = SimplePublisher()

    try:
        # Keep the node running until interrupted
        rclpy.spin(simple_publisher)
    except KeyboardInterrupt:
        simple_publisher.get_logger().info('Keyboard interrupt received, shutting down')
    finally:
        # Clean up
        simple_publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()