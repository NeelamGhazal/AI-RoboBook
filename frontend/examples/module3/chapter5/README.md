# Module 3 Chapter 5: Perception Pipeline Code Examples

Complete perception and navigation pipeline integrating Isaac ROS Visual SLAM with Nav2 for autonomous robot navigation.

## Overview

This example demonstrates:
- Isaac ROS Visual SLAM for localization
- Nav2 navigation stack for path planning
- Autonomous waypoint navigation
- Integration with Isaac Sim or real robots

## Prerequisites

### Hardware
- NVIDIA GPU (RTX 3060 or better)
- Ubuntu 22.04 LTS
- 32GB RAM (64GB recommended)
- 50GB free disk space

### Software
- ROS 2 Humble
- Isaac ROS Visual SLAM
- Nav2 Navigation Stack
- Isaac Sim (optional, for simulation)

## Installation

### 1. Install ROS 2 Humble

```bash
# Add ROS 2 repository
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

# Install ROS 2 Humble
sudo apt update
sudo apt install ros-humble-desktop

# Source ROS 2
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 2. Install Isaac ROS Visual SLAM

Follow the official Isaac ROS installation guide:
https://nvidia-isaac-ros.github.io/getting_started/index.html

```bash
# Create workspace
mkdir -p ~/isaac_ros_ws/src
cd ~/isaac_ros_ws/src

# Clone Isaac ROS Visual SLAM
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_visual_slam.git

# Install dependencies
cd ~/isaac_ros_ws
rosdep install --from-paths src --ignore-src -r -y

# Build
colcon build --symlink-install
source install/setup.bash
```

### 3. Install Nav2

```bash
sudo apt install ros-humble-navigation2
sudo apt install ros-humble-nav2-bringup
sudo apt install ros-humble-nav2-simple-commander
```

### 4. Install Python Dependencies

```bash
cd module3/chapter5
pip install -r requirements.txt
```

## Usage

### Quick Start (Simulation)

1. **Launch Isaac Sim** (if using simulation):
```bash
# Start Isaac Sim with your custom scene
~/.local/share/ov/pkg/isaac_sim-2023.1.1/python.sh warehouse_scene.py
```

2. **Launch Isaac ROS VSLAM**:
```bash
# Terminal 2
source ~/isaac_ros_ws/install/setup.bash
ros2 launch isaac_vslam_launch.py
```

3. **Launch Nav2**:
```bash
# Terminal 3
ros2 launch nav2_bringup navigation_launch.py \
    use_sim_time:=False \
    params_file:=/path/to/nav2_params.yaml
```

4. **Run Navigation Demo**:
```bash
# Terminal 4
python3 perception_pipeline.py
```

### Visualization

Launch RViz2 to visualize the robot state:

```bash
rviz2
```

Add the following displays:
- **TF**: Shows coordinate frames
- **Map**: Global costmap
- **Local Costmap**: Dynamic obstacles
- **Global Path**: Planned path
- **Local Path**: Current trajectory
- **Robot Model**: 3D robot visualization

### Configuration

#### Isaac ROS VSLAM Parameters

Edit `isaac_vslam_launch.py` to adjust:
- `num_features`: Number of features to track (default: 800)
- `max_frame_rate`: Maximum camera frame rate (default: 30 Hz)
- `enable_imu_fusion`: Enable IMU fusion (default: false)

#### Nav2 Parameters

Create `nav2_params.yaml` with your robot-specific parameters:
- `robot_radius`: Robot collision radius
- `max_vel_x`: Maximum linear velocity
- `inflation_radius`: Safety margin around obstacles

See the full `nav2_params.yaml` example in Chapter 5 documentation.

## File Descriptions

| File | Description |
|------|-------------|
| `isaac_vslam_launch.py` | Launch file for Isaac ROS Visual SLAM |
| `perception_pipeline.py` | Waypoint navigation demo script |
| `requirements.txt` | Python and ROS 2 dependencies |
| `README.md` | This file |

## Troubleshooting

### Issue: VSLAM tracking loss

**Symptoms**: Odometry stops updating, robot drifts

**Solutions**:
- Ensure adequate lighting in environment
- Add visual features (posters, patterns) to walls
- Reduce robot speed
- Enable IMU fusion

### Issue: Nav2 cannot find path

**Symptoms**: Planning fails, no path displayed

**Solutions**:
- Verify map frame is published by VSLAM
- Check global costmap is populated
- Reduce `inflation_radius` if too conservative
- Ensure goal is reachable (not in obstacle)

### Issue: Robot oscillates during navigation

**Symptoms**: Robot wobbles, unstable motion

**Solutions**:
- Reduce `max_vel_theta` in controller config
- Increase `xy_goal_tolerance`
- Adjust DWB critic weights (PathAlign, GoalAlign)
- Increase `sim_time` for better trajectory prediction

### Issue: High CPU/GPU usage

**Symptoms**: System lag, thermal throttling

**Solutions**:
- Reduce camera resolution (640x480 instead of 1280x720)
- Lower `max_frame_rate` to 20 Hz
- Reduce `num_features` to 500
- Decrease Nav2 `controller_frequency` to 10 Hz

## Performance Benchmarks

Typical performance on NVIDIA Jetson AGX Orin:

| Component | Frame Rate | Latency | CPU Usage | GPU Usage |
|-----------|------------|---------|-----------|-----------|
| **Isaac ROS VSLAM** | 30 Hz | 15ms | 15% | 40% |
| **Nav2 Planner** | 1 Hz | 50ms | 10% | 0% |
| **Nav2 Controller** | 20 Hz | 10ms | 5% | 0% |
| **Total Pipeline** | 30 Hz | 75ms | 30% | 40% |

## Extensions

### Add Object Detection

Integrate YOLO or other detectors:

```python
# Add to perception_pipeline.py
from isaac_ros_dnn_inference import TensorRTInference

detector = TensorRTInference(
    model_path="/models/yolov8n.onnx",
    input_topic="/camera/rgb",
    output_topic="/detections"
)
```

### Multi-Robot Coordination

Use unique namespaces for each robot:

```bash
ros2 launch isaac_vslam_launch.py namespace:=robot1
ros2 launch isaac_vslam_launch.py namespace:=robot2
```

### Real Robot Deployment

1. Replace simulation topics with real sensor topics
2. Calibrate cameras (intrinsics and extrinsics)
3. Add safety features (cliff detection, emergency stop)
4. Test in controlled environment first

## References

- [Isaac ROS Documentation](https://nvidia-isaac-ros.github.io/)
- [Nav2 Documentation](https://navigation.ros.org/)
- [ROS 2 Humble Documentation](https://docs.ros.org/en/humble/)
- [RoboBook Module 3 Full Tutorial](../../docs/module3/)

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-repo/issues
- RoboBook Discord: https://discord.gg/robobook
- ROS Answers: https://answers.ros.org/

---

**RoboBook Team** | Module 3: Advanced ROS 2 Programming
