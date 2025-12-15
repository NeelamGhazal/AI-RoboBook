---
sidebar_label: 'Chapter 4: Python-ROS 2 Integration'
sidebar_position: 4
---

# Chapter 4: Python-ROS 2 Integration

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand the rclpy library and its role in Python-ROS 2 integration
- Create custom message and service definitions
- Implement advanced node features like parameters and timers
- Use launch files to run multiple nodes together
- Debug Python ROS 2 nodes effectively

## Introduction to rclpy

The `rclpy` library is the Python client library for ROS 2. It provides the Python API for creating ROS 2 nodes, publishers, subscribers, services, and other ROS 2 entities.

### Key Components of rclpy

- `rclpy.node.Node`: Base class for creating nodes
- `rclpy.init()`: Initializes the ROS 2 client library
- `rclpy.spin()`: Processes callbacks until shutdown
- `rclpy.shutdown()`: Shuts down the ROS 2 client library

## Advanced Node Features

### Parameters

Parameters allow nodes to be configured at runtime. Here's how to implement parameters in a node:

```python
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter


class ParameterNode(Node):
    def __init__(self):
        super().__init__('parameter_node')

        # Declare parameters with default values
        self.declare_parameter('robot_name', 'my_robot')
        self.declare_parameter('max_velocity', 1.0)
        self.declare_parameter('use_camera', True)

        # Get parameter values
        self.robot_name = self.get_parameter('robot_name').value
        self.max_velocity = self.get_parameter('max_velocity').value
        self.use_camera = self.get_parameter('use_camera').value

        # Register callback for parameter changes
        self.add_on_set_parameters_callback(self.parameters_callback)

        self.get_logger().info(f'Initialized with robot_name: {self.robot_name}')

    def parameters_callback(self, params):
        """Callback for parameter changes."""
        for param in params:
            if param.name == 'max_velocity' and param.type_ == Parameter.Type.DOUBLE:
                if param.value > 5.0:
                    return SetParametersResult(successful=False, reason='Max velocity too high')
        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    node = ParameterNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

### Advanced Timers

Timers can be configured with different rates and callback groups:

```python
import rclpy
from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor


class AdvancedTimerNode(Node):
    def __init__(self):
        super().__init__('advanced_timer_node')

        # Create different callback groups
        self.group1 = MutuallyExclusiveCallbackGroup()
        self.group2 = MutuallyExclusiveCallbackGroup()

        # Create timers with different periods and groups
        self.timer1 = self.create_timer(
            0.5,  # 2 Hz
            self.timer1_callback,
            callback_group=self.group1
        )

        self.timer2 = self.create_timer(
            1.0,  # 1 Hz
            self.timer2_callback,
            callback_group=self.group2
        )

    def timer1_callback(self):
        self.get_logger().info('Timer 1 callback')

    def timer2_callback(self):
        self.get_logger().info('Timer 2 callback')


def main(args=None):
    rclpy.init(args=args)
    node = AdvancedTimerNode()

    # Use multi-threaded executor to handle different callback groups
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

## Custom Messages and Services

### Creating Custom Messages

To create custom messages, define `.msg` files in your package's `msg/` directory:

```
# Point2D.msg
float64 x
float64 y
```

```
# RobotStatus.msg
string robot_name
float64 battery_level
bool is_moving
int8[] joint_angles
```

### Creating Custom Services

Define `.srv` files in your package's `srv/` directory:

```
# AddTwoFloats.srv
float64 a
float64 b
---
float64 sum
```

After creating these files, update your `package.xml` to include the message generation dependencies:

```xml
<build_depend>rosidl_default_generators</build_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

And update your `setup.py`:

```python
from setuptools import setup
from rosidl_default_generators import generate_interfaces

setup(
    # ... other setup parameters ...
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include message files
        ('share/' + package_name + '/msg', ['msg/Point2D.msg', 'msg/RobotStatus.msg']),
        ('share/' + package_name + '/srv', ['srv/AddTwoFloats.srv']),
    ],
    # ... other setup parameters ...
)
```

## Launch Files

Launch files allow you to start multiple nodes with a single command. Create launch files in your package's `launch/` directory:

```python
# my_launch_file.py
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Declare launch arguments
    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='default_robot',
        description='Name of the robot'
    )

    # Get launch configuration
    robot_name = LaunchConfiguration('robot_name')

    # Define nodes
    publisher_node = Node(
        package='my_package',
        executable='simple_publisher',
        name='publisher_node',
        parameters=[{'robot_name': robot_name}]
    )

    subscriber_node = Node(
        package='my_package',
        executable='simple_subscriber',
        name='subscriber_node',
        parameters=[{'robot_name': robot_name}]
    )

    return LaunchDescription([
        robot_name_arg,
        publisher_node,
        subscriber_node
    ])
```

To run the launch file:

```bash
ros2 launch my_package my_launch_file.py robot_name:=my_robot
```

## Actions

Actions are used for long-running tasks that provide feedback:

```python
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self.execute_callback,
            callback_group=rclpy.callback_groups.ReentrantCallbackGroup(),
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback)

    def goal_callback(self, goal_request):
        """Accept or reject a client request to begin an action."""
        self.get_logger().info('Received goal request')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """Accept or reject a client request to cancel an action."""
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        """Execute the goal."""
        self.get_logger().info('Executing goal...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return Fibonacci.Result()

            feedback_msg.sequence.append(
                feedback_msg.sequence[i] + feedback_msg.sequence[i-1])

            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f'Publishing feedback: {feedback_msg.sequence}')

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        self.get_logger().info(f'Returning result: {result.sequence}')

        return result


def main(args=None):
    rclpy.init(args=args)
    action_server = FibonacciActionServer()

    try:
        rclpy.spin(action_server)
    except KeyboardInterrupt:
        pass
    finally:
        action_server.destroy_node()
        rclpy.shutdown()
```

## Debugging Python ROS 2 Nodes

### Common Debugging Techniques

1. **Use Logging**: Use appropriate log levels (info, warn, error, debug)
2. **ROS 2 Tools**: Use `ros2 node`, `ros2 topic`, `ros2 service` commands
3. **Python Debugging**: Use `pdb` or IDE debuggers
4. **RViz**: Visualize robot state and sensor data

### Debugging Example

```python
import rclpy
from rclpy.node import Node
import pdb  # Python debugger


class DebugNode(Node):
    def __init__(self):
        super().__init__('debug_node')
        self.publisher = self.create_publisher(String, 'debug_topic', 10)

        # Set up a timer for debugging
        self.timer = self.create_timer(1.0, self.debug_callback)
        self.counter = 0

    def debug_callback(self):
        # Use pdb.set_trace() to pause execution for debugging
        # pdb.set_trace()

        self.get_logger().debug(f'Debug info: counter = {self.counter}')
        self.get_logger().info(f'Info: publishing message {self.counter}')

        # Add debug conditions
        if self.counter == 5:
            self.get_logger().warn('Counter reached 5 - special condition')

        self.counter += 1


def main(args=None):
    rclpy.init(args=args)
    node = DebugNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node interrupted by user')
    finally:
        node.destroy_node()
        rclpy.shutdown()
```

## Performance Optimization

### Efficient Message Handling

```python
# Use appropriate QoS settings for your use case
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

# For real-time systems: reliable delivery
realtime_qos = QoSProfile(
    depth=10,
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE
)

# For best-effort systems: faster delivery
best_effort_qos = QoSProfile(
    depth=5,
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE
)

# In your node
self.publisher = self.create_publisher(String, 'topic', realtime_qos)
```

### Memory Management

```python
# Reuse message objects to reduce garbage collection
class EfficientNode(Node):
    def __init__(self):
        super().__init__('efficient_node')
        self.publisher = self.create_publisher(String, 'topic', 10)

        # Pre-allocate message object
        self.msg = String()

        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        # Reuse the same message object
        self.msg.data = f'Message number: {self.get_clock().now().nanoseconds}'
        self.publisher.publish(self.msg)
```

## Assessment Questions

1. What is the purpose of parameters in ROS 2 nodes?
2. Explain the difference between a service and an action in ROS 2.
3. How do callback groups affect node execution?
4. What are the benefits of using launch files?
5. Name three debugging techniques for Python ROS 2 nodes.

## Knowledge Check

Complete these knowledge check questions to verify your understanding:

1. **Multiple Choice**: What does rclpy stand for?
   - A) Robot Client Library for Python
   - B) ROS Client Library for Python
   - C) Robot Communication Library for Python
   - D) ROS Communication Layer for Python

   *Answer: B) ROS Client Library for Python*

2. **True/False**: Parameters can only be set when a node is launched.
   - A) True
   - B) False

   *Answer: B) False - Parameters can be changed at runtime using ros2 param commands*

3. **Multiple Choice**: Which callback group allows callbacks to be executed in parallel?
   - A) MutuallyExclusiveCallbackGroup
   - B) ReentrantCallbackGroup
   - C) SingleThreadedCallbackGroup
   - D) MultiThreadedCallbackGroup

   *Answer: B) ReentrantCallbackGroup*

4. **Short Answer**: Explain when you would use an action instead of a service in ROS 2.

   *Answer: Use an action for long-running tasks that need to provide feedback during execution and have cancelation capability, such as navigation or manipulation tasks. Use a service for simple request-response operations.*

5. **Scenario**: You need to start a robot with 10 different nodes that all need to start simultaneously. What would be the best approach?

   *Answer: Create a launch file that defines all 10 nodes and use ros2 launch to start them all at once with a single command.*

## References

- [rclpy Documentation](https://docs.ros.org/en/humble/p/rclpy/)
- [ROS 2 Launch System](https://docs.ros.org/en/humble/p/launch/)
- [ROS 2 Actions](https://docs.ros.org/en/humble/p/action-tutorials/)