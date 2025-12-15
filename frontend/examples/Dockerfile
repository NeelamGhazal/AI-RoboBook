# RoboBook Docker Testing Environment
# Base: ROS 2 Humble + Ubuntu 22.04 Jammy

FROM osrf/ros:humble-desktop-full-jammy

# Set working directory
WORKDIR /workspace

# Install Python dependencies for testing and development
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-pytest \
    python3-flake8 \
    && rm -rf /var/lib/apt/lists/*

# Copy code examples into container
COPY . /workspace

# Source ROS 2 Humble setup in bashrc
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

# Default command: bash shell
CMD ["/bin/bash"]
