# Troubleshooting

## Common ROS 2 Issues

### Package Not Found
**Problem**: `ros2 run package_name executable` returns "Package not found"
**Solution**:
1. Source ROS 2 setup:
   ```bash
   source /opt/ros/humble/setup.bash
   ```
2. Source your workspace:
   ```bash
   cd ~/ros2_ws
   source install/setup.bash
   ```

### DDS Communication Issues
**Problem**: Nodes cannot communicate across different machines
**Solution**:
1. Check network configuration:
   ```bash
   echo $ROS_DOMAIN_ID
   ```
2. Set consistent domain ID:
   ```bash
   export ROS_DOMAIN_ID=42
   ```

### Permission Errors
**Problem**: Cannot access serial devices or GPUs
**Solution**:
```bash
sudo usermod -a -G dialout $USER
sudo usermod -a -G video $USER
# Log out and back in for changes to take effect
```

## Isaac Sim Issues

### NVIDIA Driver Conflicts
**Problem**: Isaac Sim fails to launch with CUDA errors
**Solution**:
1. Check driver version:
   ```bash
   nvidia-smi
   ```
2. Update to recommended version:
   ```bash
   sudo apt install nvidia-driver-535
   sudo reboot
   ```

### CUDA Version Mismatch
**Problem**: "CUDA version mismatch" error
**Solution**:
1. Check CUDA version:
   ```bash
   nvcc --version
   ```
2. Install compatible Isaac Sim version or update CUDA

### GPU Passthrough in Docker
**Problem**: GPU not accessible in Docker container
**Solution**:
1. Install nvidia-container-toolkit:
   ```bash
   sudo apt install nvidia-container-toolkit
   sudo systemctl restart docker
   ```
2. Run with GPU support:
   ```bash
   docker run --gpus all --rm robobook-ros2-humble
   ```

## Docusaurus Issues

### Build Errors
**Problem**: `npm run build` fails with memory errors
**Solution**:
1. Increase Node.js memory limit:
   ```bash
   export NODE_OPTIONS="--max-old-space-size=4096"
   npm run build
   ```

### Local Development Server Issues
**Problem**: `npm start` hangs or fails
**Solution**:
1. Clear cache:
   ```bash
   npm run clear
   ```
2. Reinstall dependencies:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   npm start
   ```

## Docker Issues

### Container Build Failures
**Problem**: `docker build` fails with permission errors
**Solution**:
1. Check Docker permissions:
   ```bash
   sudo usermod -aG docker $USER
   ```
2. Log out and log back in

### Image Pull Failures
**Problem**: `docker pull` fails with network errors
**Solution**:
1. Check network connection
2. Configure Docker with proxy if needed:
   ```bash
   mkdir -p ~/.docker/config.json
   # Add proxy configuration if required
   ```

## Python Environment Issues

### Package Installation Failures
**Problem**: `pip install` fails with permission errors
**Solution**:
1. Use virtual environment:
   ```bash
   python3 -m venv robobook_env
   source robobook_env/bin/activate
   pip install package_name
   ```

### Import Errors
**Problem**: Python cannot import ROS 2 packages
**Solution**:
1. Ensure ROS 2 is sourced:
   ```bash
   source /opt/ros/humble/setup.bash
   source ~/ros2_ws/install/setup.bash
   ```

## Network and Connectivity

### Internet Connection Issues
**Problem**: Cannot download packages or dependencies
**Solution**:
1. Check internet connection
2. Configure proxy if needed:
   ```bash
   export http_proxy=http://proxy.company.com:8080
   export https_proxy=http://proxy.company.com:8080
   ```

### Firewall Blocking
**Problem**: Cannot connect to external services
**Solution**:
1. Check firewall settings:
   ```bash
   sudo ufw status
   ```
2. Allow required ports:
   ```bash
   sudo ufw allow 80,443,11311,11345:11347/tcp
   ```

## Hardware Troubleshooting

### RealSense Camera Issues
**Problem**: Camera not detected or depth data unavailable
**Solution**:
1. Check camera connection:
   ```bash
   rs-enumerate-devices
   ```
2. Update firmware:
   ```bash
   rs-fw-update
   ```

### Jetson Platform Issues
**Problem**: Jetson not booting or performance issues
**Solution**:
1. Check power supply (5V/4A minimum)
2. Monitor temperature:
   ```bash
   sudo tegrastats
   ```
3. Ensure proper cooling solution

## Performance Optimization

### Slow Build Times
**Problem**: Docusaurus build takes longer than 5 minutes
**Solution**:
1. Enable caching:
   ```bash
   npm run build -- --cache
   ```
2. Use faster storage (SSD vs HDD)

### High Memory Usage
**Problem**: System becomes unresponsive during builds
**Solution**:
1. Close unnecessary applications
2. Increase swap space:
   ```bash
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## Getting Help

If you encounter issues not covered here:

1. Check the [ROS 2 Documentation](https://docs.ros.org/)
2. Visit the [NVIDIA Isaac Forum](https://forums.developer.nvidia.com/c/isaac/)
3. Search GitHub Issues in the RoboBook repository
4. Create a new issue with detailed error messages and system information