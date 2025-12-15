---
sidebar_label: 'Chapter 5: Hands-on Custom Environment'
sidebar_position: 5
---

# Chapter 5: Hands-on - Creating a Custom Simulation Environment

⏱️ **Estimated Time**: 60 minutes

## Learning Objectives

By the end of this hands-on tutorial, you will be able to:
- Create a custom Gazebo world file from scratch
- Design and place environmental elements (walls, obstacles, lighting)
- Integrate sensors into a robot model
- Spawn robots programmatically using ROS 2 services
- Test and validate your simulation environment
- Troubleshoot common Gazebo issues

## Prerequisites

### Required Software

- ✅ ROS 2 Humble installed
- ✅ Gazebo Garden or Fortress
- ✅ Python 3.8+
- ✅ Text editor (VS Code recommended)

### Required Knowledge

- Basic ROS 2 concepts (Chapter 1-2 of Module 1)
- URDF/SDF syntax (Module 2, Chapter 3)
- Linux command line basics

### Verification

```bash
# Verify ROS 2 installation
ros2 --version

# Verify Gazebo installation
gazebo --version

# Check Gazebo plugins
ros2 pkg list | grep gazebo

# Expected output includes:
# gazebo_ros
# gazebo_ros_pkgs
# gazebo_plugins
```

## Project Overview

In this tutorial, we'll create a custom warehouse simulation environment with:
- **Custom world**: Indoor warehouse with walls and obstacles
- **Lighting**: Realistic lighting setup
- **Robot**: Mobile robot with camera and LiDAR sensors
- **Spawning script**: Python script to programmatically spawn robots
- **Testing framework**: Validation of sensors and robot movement

### Project Structure

```
~/custom_gazebo_ws/
├── src/
│   └── warehouse_simulation/
│       ├── worlds/
│       │   └── warehouse.world
│       ├── models/
│       │   └── mobile_robot/
│       │       ├── model.sdf
│       │       └── model.config
│       ├── launch/
│       │   ├── warehouse.launch.py
│       │   └── spawn_robot.launch.py
│       ├── scripts/
│       │   └── spawn_robot.py
│       ├── package.xml
│       └── setup.py
└── install/
```

## Part 1: Workspace Setup (5 minutes)

### Step 1: Create Workspace

```bash
# Create workspace
mkdir -p ~/custom_gazebo_ws/src
cd ~/custom_gazebo_ws/src

# Create package
ros2 pkg create warehouse_simulation \
    --build-type ament_python \
    --dependencies rclpy gazebo_ros

# Create directory structure
cd warehouse_simulation
mkdir -p worlds models launch scripts
```

### Step 2: Configure Package

Edit `package.xml` to add dependencies:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>warehouse_simulation</name>
  <version>0.0.1</version>
  <description>Custom warehouse simulation environment</description>
  <maintainer email="your@email.com">Your Name</maintainer>
  <license>MIT</license>

  <depend>rclpy</depend>
  <depend>gazebo_ros</depend>
  <depend>gazebo_ros_pkgs</depend>
  <depend>geometry_msgs</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

Update `setup.py`:

```python
from setuptools import setup
import os
from glob import glob

package_name = 'warehouse_simulation'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        (os.path.join('share', package_name, 'models/mobile_robot'), glob('models/mobile_robot/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your@email.com',
    description='Custom warehouse simulation',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'spawn_robot = warehouse_simulation.spawn_robot:main'
        ],
    },
)
```

## Part 2: Creating the World File (15 minutes)

### Step 3: Basic World Structure

Create `worlds/warehouse.world`:

```xml
<?xml version="1.0"?>
<sdf version="1.8">
  <world name="warehouse">
    <!-- Physics settings -->
    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>

    <!-- Scene settings -->
    <scene>
      <ambient>0.4 0.4 0.4 1</ambient>
      <background>0.7 0.7 0.7 1</background>
      <shadows>true</shadows>
    </scene>

    <!-- Sun (directional light) -->
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Overhead warehouse lights -->
    <light type="point" name="warehouse_light_1">
      <pose>5 5 5 0 0 0</pose>
      <diffuse>1 1 1 1</diffuse>
      <specular>0.1 0.1 0.1 1</specular>
      <attenuation>
        <range>20</range>
        <constant>0.5</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <cast_shadows>false</cast_shadows>
    </light>

    <light type="point" name="warehouse_light_2">
      <pose>-5 5 5 0 0 0</pose>
      <diffuse>1 1 1 1</diffuse>
      <specular>0.1 0.1 0.1 1</specular>
      <attenuation>
        <range>20</range>
      </attenuation>
    </light>

    <!-- Ground plane -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>100</mu>
                <mu2>50</mu2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.5 0.5 0.5 1</ambient>
            <diffuse>0.5 0.5 0.5 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Warehouse walls -->
    <model name="wall_north">
      <static>true</static>
      <pose>0 10 1.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>20 0.2 3</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>20 0.2 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.7 0.7 0.7 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <model name="wall_south">
      <static>true</static>
      <pose>0 -10 1.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>20 0.2 3</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>20 0.2 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.7 0.7 0.7 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <model name="wall_east">
      <static>true</static>
      <pose>10 0 1.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.2 20 3</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.2 20 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.7 0.7 0.7 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <model name="wall_west">
      <static>true</static>
      <pose>-10 0 1.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>0.2 20 3</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>0.2 20 3</size>
            </box>
          </geometry>
          <material>
            <ambient>0.7 0.7 0.7 1</ambient>
            <diffuse>0.7 0.7 0.7 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- Obstacles (boxes on pallets) -->
    <model name="obstacle_1">
      <static>true</static>
      <pose>3 3 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.5 0.2 1</ambient>
            <diffuse>0.8 0.5 0.2 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <model name="obstacle_2">
      <static>true</static>
      <pose>-3 -3 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>1 1 1</size>
            </box>
          </geometry>
          <material>
            <ambient>0.8 0.5 0.2 1</ambient>
            <diffuse>0.8 0.5 0.2 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <!-- ROS 2 time publisher plugin -->
    <plugin name="gazebo_ros_state" filename="libgazebo_ros_state.so">
      <ros>
        <namespace>/gazebo</namespace>
      </ros>
      <update_rate>10.0</update_rate>
    </plugin>

  </world>
</sdf>
```

## Part 3: Creating the Robot Model (20 minutes)

### Step 4: Robot Model with Sensors

Create `models/mobile_robot/model.config`:

```xml
<?xml version="1.0"?>
<model>
  <name>Mobile Robot</name>
  <version>1.0</version>
  <sdf version="1.8">model.sdf</sdf>

  <author>
    <name>Your Name</name>
    <email>your@email.com</email>
  </author>

  <description>
    Mobile robot with differential drive, camera, and LiDAR
  </description>
</model>
```

Create `models/mobile_robot/model.sdf`:

```xml
<?xml version="1.0"?>
<sdf version="1.8">
  <model name="mobile_robot">
    <pose>0 0 0.1 0 0 0</pose>

    <!-- Base link -->
    <link name="base_link">
      <inertial>
        <mass>10.0</mass>
        <inertia>
          <ixx>0.166</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.166</iyy>
          <iyz>0</iyz>
          <izz>0.166</izz>
        </inertia>
      </inertial>

      <collision name="collision">
        <geometry>
          <box>
            <size>0.5 0.3 0.2</size>
          </box>
        </geometry>
      </collision>

      <visual name="visual">
        <geometry>
          <box>
            <size>0.5 0.3 0.2</size>
          </box>
        </geometry>
        <material>
          <ambient>0.2 0.2 0.8 1</ambient>
          <diffuse>0.2 0.2 0.8 1</diffuse>
        </material>
      </visual>

      <!-- Camera sensor -->
      <sensor name="camera" type="camera">
        <pose>0.25 0 0.1 0 0 0</pose>
        <update_rate>30</update_rate>
        <camera>
          <horizontal_fov>1.047</horizontal_fov>
          <image>
            <width>640</width>
            <height>480</height>
            <format>R8G8B8</format>
          </image>
          <clip>
            <near>0.1</near>
            <far>100</far>
          </clip>
          <noise>
            <type>gaussian</type>
            <mean>0.0</mean>
            <stddev>0.007</stddev>
          </noise>
        </camera>
        <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
          <ros>
            <namespace>/mobile_robot</namespace>
            <remapping>camera/image_raw:=camera/image_raw</remapping>
            <remapping>camera/camera_info:=camera/camera_info</remapping>
          </ros>
          <camera_name>camera</camera_name>
          <frame_name>camera_link</frame_name>
        </plugin>
      </sensor>

      <!-- LiDAR sensor -->
      <sensor name="lidar" type="ray">
        <pose>0 0 0.15 0 0 0</pose>
        <update_rate>10</update_rate>
        <ray>
          <scan>
            <horizontal>
              <samples>360</samples>
              <resolution>1</resolution>
              <min_angle>-3.14159</min_angle>
              <max_angle>3.14159</max_angle>
            </horizontal>
          </scan>
          <range>
            <min>0.12</min>
            <max>10.0</max>
            <resolution>0.01</resolution>
          </range>
          <noise>
            <type>gaussian</type>
            <mean>0.0</mean>
            <stddev>0.01</stddev>
          </noise>
        </ray>
        <plugin name="lidar_controller" filename="libgazebo_ros_ray_sensor.so">
          <ros>
            <namespace>/mobile_robot</namespace>
            <remapping>~/out:=scan</remapping>
          </ros>
          <output_type>sensor_msgs/LaserScan</output_type>
          <frame_name>lidar_link</frame_name>
        </plugin>
      </sensor>
    </link>

    <!-- Left wheel -->
    <link name="left_wheel">
      <pose>0 0.2 0.05 -1.5708 0 0</pose>
      <inertial>
        <mass>0.5</mass>
        <inertia>
          <ixx>0.001</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.001</iyy>
          <iyz>0</iyz>
          <izz>0.001</izz>
        </inertia>
      </inertial>

      <collision name="collision">
        <geometry>
          <cylinder>
            <radius>0.05</radius>
            <length>0.05</length>
          </cylinder>
        </geometry>
        <surface>
          <friction>
            <ode>
              <mu>1.0</mu>
              <mu2>1.0</mu2>
            </ode>
          </friction>
        </surface>
      </collision>

      <visual name="visual">
        <geometry>
          <cylinder>
            <radius>0.05</radius>
            <length>0.05</length>
          </cylinder>
        </geometry>
        <material>
          <ambient>0.2 0.2 0.2 1</ambient>
          <diffuse>0.2 0.2 0.2 1</diffuse>
        </material>
      </visual>
    </link>

    <!-- Right wheel -->
    <link name="right_wheel">
      <pose>0 -0.2 0.05 -1.5708 0 0</pose>
      <inertial>
        <mass>0.5</mass>
        <inertia>
          <ixx>0.001</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.001</iyy>
          <iyz>0</iyz>
          <izz>0.001</izz>
        </inertia>
      </inertial>

      <collision name="collision">
        <geometry>
          <cylinder>
            <radius>0.05</radius>
            <length>0.05</length>
          </cylinder>
        </geometry>
        <surface>
          <friction>
            <ode>
              <mu>1.0</mu>
              <mu2>1.0</mu2>
            </ode>
          </friction>
        </surface>
      </collision>

      <visual name="visual">
        <geometry>
          <cylinder>
            <radius>0.05</radius>
            <length>0.05</length>
          </cylinder>
        </geometry>
        <material>
          <ambient>0.2 0.2 0.2 1</ambient>
          <diffuse>0.2 0.2 0.2 1</diffuse>
        </material>
      </visual>
    </link>

    <!-- Joints -->
    <joint name="left_wheel_joint" type="revolute">
      <parent>base_link</parent>
      <child>left_wheel</child>
      <axis>
        <xyz>0 0 1</xyz>
      </axis>
    </joint>

    <joint name="right_wheel_joint" type="revolute">
      <parent>base_link</parent>
      <child>right_wheel</child>
      <axis>
        <xyz>0 0 1</xyz>
      </axis>
    </joint>

    <!-- Differential drive plugin -->
    <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
      <ros>
        <namespace>/mobile_robot</namespace>
      </ros>

      <update_rate>50</update_rate>

      <left_joint>left_wheel_joint</left_joint>
      <right_joint>right_wheel_joint</right_joint>

      <wheel_separation>0.4</wheel_separation>
      <wheel_diameter>0.1</wheel_diameter>

      <max_wheel_torque>20</max_wheel_torque>
      <max_wheel_acceleration>1.0</max_wheel_acceleration>

      <publish_odom>true</publish_odom>
      <publish_odom_tf>true</publish_odom_tf>
      <publish_wheel_tf>false</publish_wheel_tf>

      <odometry_frame>odom</odometry_frame>
      <robot_base_frame>base_link</robot_base_frame>
    </plugin>

  </model>
</sdf>
```

## Part 4: Launch Files and Scripts (10 minutes)

### Step 5: Create Launch File

Create `launch/warehouse.launch.py`:

```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('warehouse_simulation')
    world_file = os.path.join(pkg_share, 'worlds', 'warehouse.world')

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'),
                        'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={'world': world_file}.items()
    )

    return LaunchDescription([
        gazebo
    ])
```

### Step 6: Robot Spawning Script

Create `warehouse_simulation/spawn_robot.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity
from geometry_msgs.msg import Pose
import os
from ament_index_python.packages import get_package_share_directory


class RobotSpawner(Node):
    def __init__(self):
        super().__init__('robot_spawner')

        # Create service client
        self.client = self.create_client(SpawnEntity, '/spawn_entity')

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn_entity service...')

    def spawn_robot(self, robot_name, x=0.0, y=0.0, z=0.1):
        """Spawn robot at specified position"""

        # Get model path
        pkg_share = get_package_share_directory('warehouse_simulation')
        model_path = os.path.join(pkg_share, 'models', 'mobile_robot', 'model.sdf')

        # Read SDF file
        with open(model_path, 'r') as f:
            robot_sdf = f.read()

        # Create spawn request
        request = SpawnEntity.Request()
        request.name = robot_name
        request.xml = robot_sdf

        # Set initial pose
        request.initial_pose = Pose()
        request.initial_pose.position.x = x
        request.initial_pose.position.y = y
        request.initial_pose.position.z = z

        # Call service
        self.get_logger().info(f'Spawning {robot_name} at ({x}, {y}, {z})...')
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        if future.result() is not None:
            self.get_logger().info(f'Successfully spawned {robot_name}')
            return True
        else:
            self.get_logger().error(f'Failed to spawn {robot_name}')
            return False


def main(args=None):
    rclpy.init(args=args)

    spawner = RobotSpawner()

    # Spawn robot
    spawner.spawn_robot('mobile_robot', x=0.0, y=0.0, z=0.1)

    spawner.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

Make it executable:

```bash
chmod +x warehouse_simulation/spawn_robot.py
```

## Part 5: Build and Test (10 minutes)

### Step 7: Build the Package

```bash
# Navigate to workspace root
cd ~/custom_gazebo_ws

# Build
colcon build --packages-select warehouse_simulation

# Source the workspace
source install/setup.bash
```

### Step 8: Launch the Simulation

**Terminal 1 - Launch Gazebo**:

```bash
source ~/custom_gazebo_ws/install/setup.bash
ros2 launch warehouse_simulation warehouse.launch.py
```

**Terminal 2 - Spawn Robot**:

```bash
source ~/custom_gazebo_ws/install/setup.bash
ros2 run warehouse_simulation spawn_robot
```

### Step 9: Verify Sensors

**Check topics**:

```bash
ros2 topic list

# Expected topics:
# /mobile_robot/camera/image_raw
# /mobile_robot/camera/camera_info
# /mobile_robot/scan
# /mobile_robot/cmd_vel
# /mobile_robot/odom
# /clock
```

**View camera image**:

```bash
# Install rqt_image_view if needed
sudo apt install ros-humble-rqt-image-view

# View camera
ros2 run rqt_image_view rqt_image_view /mobile_robot/camera/image_raw
```

**View LiDAR scan**:

```bash
# Install rviz2 if needed
sudo apt install ros-humble-rviz2

# Launch RViz
rviz2
# Add LaserScan display
# Topic: /mobile_robot/scan
# Fixed Frame: odom
```

### Step 10: Test Robot Movement

**Send velocity commands**:

```bash
# Move forward
ros2 topic pub /mobile_robot/cmd_vel geometry_msgs/msg/Twist \
    "{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"

# Rotate
ros2 topic pub /mobile_robot/cmd_vel geometry_msgs/msg/Twist \
    "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}"

# Stop
ros2 topic pub /mobile_robot/cmd_vel geometry_msgs/msg/Twist \
    "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

## Troubleshooting

### Issue 1: Gazebo doesn't start

**Symptoms**: Error messages about missing plugins or world file

**Solution**:
```bash
# Check if world file exists
ls ~/custom_gazebo_ws/install/warehouse_simulation/share/warehouse_simulation/worlds/

# Verify Gazebo can find the world
gazebo ~/custom_gazebo_ws/install/warehouse_simulation/share/warehouse_simulation/worlds/warehouse.world --verbose
```

### Issue 2: Robot spawns but falls through ground

**Symptoms**: Robot position z < -1.0

**Solution**:
- Check ground plane collision is defined
- Verify robot initial pose z >= 0.1
- Increase physics solver iterations in world file

### Issue 3: Sensors not publishing

**Symptoms**: No topics for camera or LiDAR

**Solution**:
```bash
# Check Gazebo plugins loaded
ros2 run gazebo_ros spawn_entity.py --help

# Verify sensor plugins in model.sdf
grep -A 20 "sensor" models/mobile_robot/model.sdf

# Check for errors in Gazebo terminal
```

### Issue 4: Robot doesn't move

**Symptoms**: cmd_vel received but robot stationary

**Solution**:
- Verify differential drive plugin loaded
- Check wheel joint names match plugin configuration
- Increase max_wheel_torque if robot is too heavy

### Issue 5: Poor performance

**Symptoms**: Low FPS, simulation slower than real-time

**Solution**:
```bash
# Run headless (no GUI)
gazebo --verbose -s libgazebo_ros_init.so ~/custom_gazebo_ws/.../warehouse.world

# Reduce sensor rates in model.sdf
# Camera: 30 Hz → 15 Hz
# LiDAR: 10 Hz → 5 Hz
```

## Extensions and Challenges

### Challenge 1: Add More Obstacles

Add 5-10 randomly placed boxes in the warehouse.

**Hint**: Copy-paste obstacle_1 model, change name and pose.

### Challenge 2: Multi-Robot Simulation

Spawn 3 robots at different positions.

**Hint**: Modify spawn_robot.py to spawn multiple robots with unique names.

### Challenge 3: Navigation

Integrate with Nav2 for autonomous navigation.

**Steps**:
1. Install Nav2: `sudo apt install ros-humble-navigation2`
2. Create map using SLAM
3. Configure Nav2 parameters
4. Test autonomous navigation

### Challenge 4: Custom Sensor

Add a depth camera (RealSense D435i simulation).

**Hint**: Use `gazebo_ros_depth_camera` plugin.

## Assessment Checklist

✅ I can create a custom Gazebo world file
✅ I can define static obstacles and walls
✅ I can configure lighting in a simulation
✅ I can create a robot model with sensors
✅ I can spawn robots programmatically using ROS 2 services
✅ I can verify sensor data is being published
✅ I can control the robot using velocity commands
✅ I can troubleshoot common Gazebo issues
✅ I understand when to use Gazebo vs other simulators

## Summary

Congratulations! You've created a complete custom simulation environment including:

- ✅ Custom warehouse world with walls and obstacles
- ✅ Mobile robot with differential drive
- ✅ Camera sensor integration
- ✅ LiDAR sensor integration
- ✅ Programmatic robot spawning
- ✅ ROS 2 integration and testing

### Key Takeaways

1. **World files** define the simulation environment (lighting, physics, static objects)
2. **Model files** define dynamic entities (robots, sensors)
3. **Plugins** provide ROS 2 integration (publishers, subscribers, services)
4. **Testing** is crucial - verify each component incrementally
5. **Troubleshooting** follows a systematic process (check files, plugins, topics)

### Next Steps

- Complete Module 3 for advanced simulation techniques
- Explore Isaac Sim for NVIDIA-accelerated simulation
- Learn Nav2 for autonomous navigation
- Integrate computer vision algorithms with simulated sensors

## References

- [Gazebo Tutorials](https://gazebosim.org/docs)
- [SDF Format Documentation](http://sdformat.org/)
- [gazebo_ros_pkgs](https://github.com/ros-simulation/gazebo_ros_pkgs)
- [Example Worlds](https://github.com/osrf/gazebo_models)

---

**🎉 Tutorial Complete!** You now have a fully functional custom simulation environment for robotics development!