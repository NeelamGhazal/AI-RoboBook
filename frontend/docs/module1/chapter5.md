---
sidebar_label: 'Chapter 5: Hands-on - First ROS 2 Package'
sidebar_position: 5
---

# Chapter 5: Hands-on - First ROS 2 Package

⏱️ **Time Estimate: 45 minutes**

## Prerequisites

Before starting this hands-on exercise, ensure you have:
- Ubuntu 22.04 LTS installed (or WSL2/VM)
- ROS 2 Humble Hawksbill installed
- Python 3.8 or higher
- Completed Modules 1.1 through 1.4
- Basic command line familiarity

## Learning Objectives

By the end of this chapter, you will:
- Create your first ROS 2 workspace and package
- Implement a publisher and subscriber pair
- Run nodes and verify communication
- Use ROS 2 command-line tools for introspection
- Understand the complete workflow for ROS 2 development

## Introduction

This hands-on chapter will guide you through creating your first complete ROS 2 package with a publisher and subscriber. You'll build, run, and verify communication between two nodes, giving you practical experience with ROS 2's publish-subscribe communication model.

## Step 1: Create a ROS 2 Workspace

First, let's create a workspace directory for our ROS 2 packages:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

The `src` directory is where you'll place all your source code. The workspace structure is:
- `~/ros2_ws/` - Root workspace directory
- `~/ros2_ws/src/` - Source code directory
- `~/ros2_ws/build/` - Build artifacts (created after building)
- `~/ros2_ws/install/` - Installation directory (created after building)
- `~/ros2_ws/log/` - Log files (created during building)

## Step 2: Create a Package

Now create a new ROS 2 package named `robobook_examples`:

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python robobook_examples
```

This command creates a basic Python package structure. Navigate to the package directory:

```bash
cd robobook_examples
ls -la
```

You should see the package structure including `setup.py`, `package.xml`, and `robobook_examples/` directory.

## Step 3: Create Python Nodes

Create a directory for your Python scripts:

```bash
mkdir -p robobook_examples
```

Now copy the publisher code to `robobook_examples/simple_publisher.py`:

```python
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
```

Now create the subscriber code in `robobook_examples/simple_subscriber.py`:

```python
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
```

## Step 4: Update Package Setup

Now you need to make your Python scripts executable and update the setup files. First, make them executable:

```bash
chmod +x robobook_examples/simple_publisher.py
chmod +x robobook_examples/simple_subscriber.py
```

Next, update the `setup.py` file in the package root to include your scripts:

```python
from setuptools import find_packages, setup

package_name = 'robobook_examples'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robobook',
    maintainer_email='robobook@todo.todo',
    description='RoboBook example package',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_publisher = robobook_examples.simple_publisher:main',
            'simple_subscriber = robobook_examples.simple_subscriber:main',
        ],
    },
)
```

## Step 5: Build the Package

Now build your workspace:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select robobook_examples
```

If you get an error about colcon, install it:

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions
```

Then run the build command again.

## Step 6: Source the Workspace

After building, source your workspace to make the nodes available:

```bash
source ~/ros2_ws/install/setup.bash
```

## Step 7: Run the Publisher and Subscriber

Open two terminal windows or tabs.

In the first terminal, run the publisher:

```bash
source ~/ros2_ws/install/setup.bash
ros2 run robobook_examples simple_publisher
```

In the second terminal, run the subscriber:

```bash
source ~/ros2_ws/install/setup.bash
ros2 run robobook_examples simple_subscriber
```

You should see the publisher sending messages and the subscriber receiving them!

## Step 8: Use ROS 2 Command-Line Tools

While your nodes are running, open a third terminal and try these commands:

List active nodes:
```bash
ros2 node list
```

Check node information:
```bash
ros2 node info /simple_publisher
ros2 node info /simple_subscriber
```

List active topics:
```bash
ros2 topic list
```

Check topic information:
```bash
ros2 topic info /chatter
```

Monitor messages on the topic:
```bash
ros2 topic echo /chatter
```

## Expected Output

**Publisher Terminal:**
```
[INFO] [1699123456.789] [simple_publisher]: Simple Publisher node initialized
[INFO] [1699123457.289] [simple_publisher]: Publishing: "Hello World: 0"
[INFO] [1699123457.789] [simple_publisher]: Publishing: "Hello World: 1"
[INFO] [1699123458.289] [simple_publisher]: Publishing: "Hello World: 2"
...
```

**Subscriber Terminal:**
```
[INFO] [1699123457.290] [simple_subscriber]: Simple Subscriber node initialized
[INFO] [1699123457.290] [simple_subscriber]: I heard: "Hello World: 0"
[INFO] [1699123457.789] [simple_subscriber]: I heard: "Hello World: 1"
[INFO] [1699123458.289] [simple_subscriber]: I heard: "Hello World: 2"
...
```

## Troubleshooting

### Common Issues and Solutions

1. **"command 'colcon' not found"**
   - Install colcon: `sudo apt install python3-colcon-common-extensions`

2. **"ModuleNotFoundError: No module named 'rclpy'"**
   - Ensure ROS 2 is sourced: `source /opt/ros/humble/setup.bash`

3. **Nodes don't see each other**
   - Check that both terminals have the workspace sourced
   - Verify both nodes have unique names
   - Check ROS_DOMAIN_ID: `echo $ROS_DOMAIN_ID` (should be same in both terminals)

4. **"ament_python" build type error**
   - Install ament: `sudo apt install python3-ament-build`

### Verification Steps

1. Check if both nodes are running:
   ```bash
   ros2 node list
   ```

2. Verify topic communication:
   ```bash
   ros2 topic echo /chatter
   ```

3. Check topic statistics:
   ```bash
   ros2 topic hz /chatter
   ```

## Assessment Checklist

✅ I can create a ROS 2 workspace and package
✅ I can implement a publisher node that sends messages
✅ I can implement a subscriber node that receives messages
✅ I can build my ROS 2 package successfully
✅ I can run publisher and subscriber nodes simultaneously
✅ I can verify communication between nodes using command-line tools
✅ I can troubleshoot basic ROS 2 communication issues

## Knowledge Check

Complete these knowledge check questions to verify your understanding:

1. **Multiple Choice**: What command is used to create a new ROS 2 package?
   - A) `ros2 create pkg`
   - B) `ros2 pkg create`
   - C) `create_ros2_package`
   - D) `ros2 new package`

   *Answer: B) `ros2 pkg create`*

2. **True/False**: The `colcon build` command builds all packages in the workspace by default.
   - A) True
   - B) False

   *Answer: A) True - colcon build will build all packages in the workspace unless specific packages are specified*

3. **Multiple Choice**: What is the purpose of the `setup.py` file in a ROS 2 Python package?
   - A) To define entry points for executable nodes
   - B) To specify package dependencies
   - C) To configure the build process
   - D) All of the above

   *Answer: D) All of the above*

4. **Short Answer**: Explain the difference between `ros2 topic echo` and `ros2 topic hz` commands.

   *Answer: `ros2 topic echo` prints messages from a topic as they are received, while `ros2 topic hz` measures the frequency (rate) at which messages are published on a topic.*

5. **Scenario**: Your publisher and subscriber nodes are not communicating. List three things you would check to troubleshoot the issue.

   *Answer: Check if both terminals have the workspace sourced, verify the topic names match exactly, and ensure both nodes are running and properly configured.*

## Extensions

Try these additional exercises:
1. Modify the message content to include timestamp information
2. Create multiple subscribers to see how one publisher can serve many
3. Change the message rate and observe the effect
4. Experiment with different QoS settings for reliability
5. Add parameters to control the message content or publishing rate

## Next Steps

Now that you've created your first ROS 2 package with working publisher-subscriber communication, you're ready to explore more advanced ROS 2 concepts:

- Module 2: Learn about robot simulation with Gazebo
- Module 3: Explore NVIDIA Isaac for perception and navigation
- Advanced topics: Services, actions, parameters, and launch files

## References

- [ROS 2 Tutorials](https://docs.ros.org/en/humble/Tutorials.html)
- [Creating a Package](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Creating-A-Package-Creating-A-Package.html)
- [Python Node Examples](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html)
- [ROS 2 Command-Line Tools](https://docs.ros.org/en/humble/Reference/Tools.html)