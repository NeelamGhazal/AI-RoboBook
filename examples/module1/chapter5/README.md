# Module 1 Chapter 5: ROS 2 Publisher-Subscriber Example

This directory contains the code examples for Module 1, Chapter 5 of the RoboBook curriculum.

## Overview

This example demonstrates the fundamental ROS 2 communication pattern using a publisher and subscriber:

- `simple_publisher.py`: Publishes "Hello World" messages to the `chatter` topic
- `simple_subscriber.py`: Subscribes to the `chatter` topic and logs received messages

## Prerequisites

- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill installed
- Python 3.8 or higher
- Basic understanding of ROS 2 concepts (covered in Modules 1.1-1.4)

## Setup Instructions

1. Source your ROS 2 installation:
   ```bash
   source /opt/ros/humble/setup.bash
   ```

2. Create a ROS 2 workspace (if you don't have one):
   ```bash
   mkdir -p ~/ros2_ws/src
   cd ~/ros2_ws
   ```

3. Copy these example files to your workspace:
   ```bash
   cp -r /path/to/robobook/examples/module1/chapter5 ~/ros2_ws/src/
   ```

4. Build the workspace:
   ```bash
   cd ~/ros2_ws
   colcon build --packages-select chapter5
   source install/setup.bash
   ```

## Running the Example

### Method 1: Direct Python Execution

1. Open a terminal and run the publisher:
   ```bash
   source /opt/ros/humble/setup.bash
   python3 simple_publisher.py
   ```

2. Open another terminal and run the subscriber:
   ```bash
   source /opt/ros/humble/setup.bash
   python3 simple_subscriber.py
   ```

### Method 2: Using ROS 2 Run

1. Open a terminal and run the publisher:
   ```bash
   source /opt/ros/humble/setup.bash
   ros2 run chapter5 simple_publisher
   ```

2. Open another terminal and run the subscriber:
   ```bash
   source /opt/ros/humble/setup.bash
   ros2 run chapter5 simple_subscriber
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

### Common Issues

1. **ModuleNotFoundError: No module named 'rclpy'**
   - Ensure ROS 2 Humble is installed and sourced
   - Check that you're using Python 3

2. **Nodes cannot communicate**
   - Verify both nodes are on the same ROS_DOMAIN_ID
   - Check network configuration if running on different machines

3. **Permission errors**
   - Ensure your user is in the `dialout` group: `sudo usermod -a -G dialout $USER`

### Verification Commands

Check if nodes are running:
```bash
ros2 node list
```

Check topic information:
```bash
ros2 topic list
ros2 topic info /chatter
```

Monitor topic messages:
```bash
ros2 topic echo /chatter
```

## Learning Outcomes

After running this example, you should understand:
- How to create basic ROS 2 publisher and subscriber nodes
- The publish-subscribe communication pattern
- How to run ROS 2 nodes
- How to verify communication between nodes
- Basic ROS 2 command-line tools

## Next Steps

- Experiment with different message types
- Add parameters to your nodes
- Try creating multiple publishers and subscribers
- Explore Quality of Service (QoS) settings

## License

This code is provided under the MIT License as part of the RoboBook curriculum.