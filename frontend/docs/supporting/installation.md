# Installation Guides

## Ubuntu 22.04 LTS Setup

### Dual-Boot Installation
1. Download Ubuntu 22.04 LTS ISO from [ubuntu.com](https://ubuntu.com/download/desktop)
2. Create bootable USB using Rufus (Windows) or Startup Disk Creator (Ubuntu)
3. Boot from USB and select "Install Ubuntu"
4. Follow installation wizard, ensuring at least 50GB free space
5. Reboot and select Ubuntu from boot menu

### WSL2 Setup (Windows)
1. Enable WSL2 in Windows Features:
   ```bash
   wsl --install
   ```
2. Install Ubuntu 22.04 from Microsoft Store
3. Launch Ubuntu and create user account
4. Update packages:
   ```bash
   sudo apt update && sudo apt upgrade
   ```

### Virtual Machine Setup
1. Install VirtualBox or VMware Workstation
2. Create new VM with:
   - 8+ GB RAM
   - 4+ CPU cores
   - 50+ GB storage
   - Enable 3D acceleration
3. Install Ubuntu 22.04 LTS

## ROS 2 Humble Hawksbill Installation

### Using apt (Recommended)
1. Set locale:
   ```bash
   sudo locale-gen en_US.UTF-8
   ```
2. Add ROS 2 apt repository:
   ```bash
   sudo apt update && sudo apt install curl gnupg lsb-release
   curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
   ```
3. Install ROS 2 packages:
   ```bash
   sudo apt update
   sudo apt install ros-humble-desktop-full
   ```
4. Source ROS 2:
   ```bash
   echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
   source ~/.bashrc
   ```

### Verification
Test installation with:
```bash
ros2 run demo_nodes_cpp talker
```

## Isaac Sim Installation

### Prerequisites
1. NVIDIA GPU with RTX series (recommended) or GTX 1080+
2. NVIDIA Driver 535 or newer
3. CUDA 11.8 or 12.x installed

### Installation Steps
1. Download Isaac Sim from [NVIDIA Developer](https://developer.nvidia.com/isaac-sim)
2. Extract to desired location
3. Run setup:
   ```bash
   cd isaac-sim
   python -m pip install -e .
   ```
4. Launch Isaac Sim:
   ```bash
   python -m omni.isaac.sim.release.setup
   ```

## Docker Installation

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker $USER
```

### Verification
```bash
docker run hello-world
```

## Python Environment Setup

### Using venv (Recommended)
```bash
python3 -m venv robobook_env
source robobook_env/bin/activate
pip install --upgrade pip
```

### Required Python Packages
```bash
pip install rclpy numpy matplotlib openai-whisper
```

## Verification Steps

### ROS 2 Test
```bash
source /opt/ros/humble/setup.bash
ros2 run demo_nodes_cpp talker &
ros2 run demo_nodes_cpp listener
```

### System Check
Run the following to verify your system is ready:
```bash
echo "ROS 2 Installation: $(ros2 --version)"
echo "Python Version: $(python3 --version)"
echo "Docker: $(docker --version)"
echo "Git: $(git --version)"
```