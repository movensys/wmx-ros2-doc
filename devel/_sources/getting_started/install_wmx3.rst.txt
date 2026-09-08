Install WMX R2 Package
========================

With the :doc:`computer_setup` complete (real-time kernel, ROS 2, and the WMX
runtime in place), build the WMX R2 packages.

Configure the environment
-------------------------

Add the following to your ``~/.bashrc``:

.. code-block:: bash

   export ROS_DOMAIN_ID=70                         #use any number
   export ROS_DISTRO=jazzy                         #support {jazzy, humble}
   export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

   source /opt/ros/$ROS_DISTRO/setup.bash
   source ~/workspaces/movensys_ws/install/setup.bash

Apply the changes:

.. code-block:: bash

   source ~/.bashrc


Install Required ROS2 Dependencies
----------------------------------------------

.. code-block:: bash

   sudo apt update
   # Install colcon and rosdep
   sudo apt install python3-colcon-common-extensions python3-rosdep
   # Install ROS2 dependencies for WMX R2 packages
   sudo apt install -y ros-${ROS_DISTRO}-graph-msgs \
                       ros-${ROS_DISTRO}-moveit-ros \
                       ros-${ROS_DISTRO}-moveit-planners \
                       ros-${ROS_DISTRO}-moveit-plugins \
                       ros-${ROS_DISTRO}-moveit-setup-assistant \
                       ros-${ROS_DISTRO}-moveit-configs-utils \
                       ros-${ROS_DISTRO}-moveit-task-constructor-core \
                       ros-${ROS_DISTRO}-ros2-control \
                       ros-${ROS_DISTRO}-ros2-controllers \
                       ros-${ROS_DISTRO}-controller-manager \
                       ros-${ROS_DISTRO}-diff-drive-controller \
                       ros-${ROS_DISTRO}-joint-trajectory-controller \
                       ros-${ROS_DISTRO}-joint-state-broadcaster \
                       ros-${ROS_DISTRO}-xacro \
                       ros-${ROS_DISTRO}-topic-tools \
                       ros-${ROS_DISTRO}-rmw-cyclonedds-cpp


Create Workspace and Build
--------------------------

**Create workspace**

.. code-block:: bash

   mkdir -p ~/workspaces/movensys_ws/src
   cd ~/workspaces/movensys_ws/src
   git clone https://github.com/movensys/wmx-r2.git

.. note::

   The manipulator and navigation descriptions are optional. If you only need
   motor control in a ROS 2 environment, you can safely ignore the missing
   ``movensys_manipulator_description`` and ``movensys_navigation_description``
   dependency errors.

   To resolve them, clone both repositories into your workspace:

   .. code-block:: bash

      cd ~/workspaces/movensys_ws/src
      git clone https://github.com/movensys/movensys-manipulator.git
      git clone https://github.com/movensys/movensys-navigation.git

**Rosdep update**

.. code-block:: bash

   sudo rosdep init   # only needed once per system
   rosdep update
   cd ~/workspaces/movensys_ws
   rosdep install --from-paths src --ignore-src -y

**Build** (``wmx_r2_package`` depends on ``wmx_r2_message``, so build the
message package first):

.. code-block:: bash

   cd ~/workspaces/movensys_ws

   # Stage 1: build the message package first
   colcon build --packages-select wmx_r2_message
   source install/setup.bash

   # Stage 2: build all remaining packages
   colcon build
   source install/setup.bash


Verify Installation
-------------------

.. code-block:: bash

   ros2 pkg list | grep wmx && ros2 pkg executables wmx_r2_package

Expected:

.. code-block:: text

   wmx_r2_control
   wmx_r2_message
   wmx_r2_package
   wmx_r2_package differential_drive_controller
   wmx_r2_package gripper_controller
   wmx_r2_package jog_keyboard_node
   wmx_r2_package joint_state_broadcaster
   wmx_r2_package joint_trajectory_controller
   wmx_r2_package wmx_core_motion_node
   wmx_r2_package wmx_engine_node
   wmx_r2_package wmx_ethercat_node
   wmx_r2_package wmx_io_node
