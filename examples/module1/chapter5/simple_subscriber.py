#!/usr/bin/env python3
"""
Simple ROS 2 Subscriber Example

This node subscribes to a topic and logs received messages.

MIT License
Copyright (c) 2025 RoboBook
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleSubscriber(Node):
    """
    A simple ROS 2 subscriber node that listens to messages from a topic.
    """

    def __init__(self):
        """
        Initialize the node with a name and create subscriber.
        """
        super().__init__('simple_subscriber')

        # Create a subscriber for String messages on the 'chatter' topic
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10  # QoS history depth
        )

        # Prevent unused variable warning
        self.subscription  # type: ignore

        # Log that the subscriber has started
        self.get_logger().info('Simple Subscriber node initialized')

    def listener_callback(self, msg):
        """
        Callback function that runs when a message is received.

        Args:
            msg: The received String message
        """
        # Log the received message
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    """
    Main function to initialize and run the subscriber node.
    """
    # Initialize ROS 2
    rclpy.init(args=args)

    # Create the subscriber node
    simple_subscriber = SimpleSubscriber()

    try:
        # Keep the node running until interrupted
        rclpy.spin(simple_subscriber)
    except KeyboardInterrupt:
        simple_subscriber.get_logger().info('Keyboard interrupt received, shutting down')
    finally:
        # Clean up
        simple_subscriber.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()