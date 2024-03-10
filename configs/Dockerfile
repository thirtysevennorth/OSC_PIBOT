# TODO remove unnecessary apt updates

# Use Ubuntu 22.04 LTS as base image
FROM ubuntu:22.04

# Set environment variables to avoid user interaction during installation
ENV DEBIAN_FRONTEND=noninteractive

## Update and install necessary packages
RUN apt update && apt upgrade -y

RUN apt install -y \
    tmux \
    curl \
    gnupg2 \
    locales \
    lsb-release \
    software-properties-common

# Enable universe repo
RUN add-apt-repository universe

# Locale stuff
RUN locale-gen en_US en_US.UTF-8 \
    && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 \
    && export LANG=en_US.UTF-8 \
    && echo $(locale)

# Add ROS2 GPG key
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o   /usr/share/keyrings/ros-archive-keyring.gpg

# Add ROS2 repos
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
         | tee /etc/apt/sources.list.d/ros2.list > /dev/null

RUN apt update && apt upgrade -y

## ROS2 packages
RUN apt install -y ros-humble-desktop
RUN apt install -y ros-humble-ros-base
RUN apt install -y ros-humble-irobot-create-msgs

# Dev tools
RUN apt install -y ros-dev-tools
RUN apt install -y build-essential python3-colcon-common-extensions python3-rosdep ros-humble-rmw-cyclonedds-cpp


# TODO needed?
RUN rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc

RUN rosdep init && rosdep update

## Create3 Sim
# RUN curl -sSL http://get.gazebosim.org | sh

## Ignition Fortress
# RUN apt update &&  apt install -y wget \
#     && sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list' \
#     && wget http://packages.osrfoundation.org/gazebo.key -O - |  apt-key add - \
#     && apt update &&  apt install -y ignition-fortress

# RUN source /opt/ros/humble/setup.bash
# RUN sh -c "source /opt/ros/humble/setup.bash"

# RUN mkdir -p /root/create3_ws/src
# RUN cd /root/create3_ws/src
# RUN git clone https://github.com/iRobotEducation/create3_sim.git
# RUN cd /root/create3_ws
# RUN rosdep install --from-path src -yi

RUN echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> /root/.bashrc
# RUN echo "export RMW_IMPLEMENTATION=rmw_fastrtps_cpp" >> /root/.bashrc

WORKDIR /root/workspace

# Set the entry point to bash
CMD ["bash"]
