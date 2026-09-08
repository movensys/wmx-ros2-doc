Install WMX R2 Package
========================

With the :doc:`computer_setup` complete (real-time kernel, ROS 2, and the WMX
runtime in place), build the WMX R2 packages.

There are two ways to do it. The container is the supported default; the
native build is there when you want the packages on the host directly.

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * -
     - Container
     - Native
   * - You run
     - ``wros <command>``
     - the command directly
   * - ROS + workspace
     - already sourced inside the container
     - sourced from your ``~/.bashrc``
   * - Root for real-time
     - ``wros`` already runs as root
     - ``sudo --preserve-env=...``

.. important::

   Either way, the WMX Runtime must be installed **on the host**
   (``/opt/wmx3/``). The container mounts it; it does not provide it. See
   :doc:`install_wmx_runtime`.

Configure the environment
-------------------------

Add the following to your ``~/.bashrc``:

.. code-block:: bash

   export ROS_DOMAIN_ID=70                         # use any number
   export ROS_DISTRO=jazzy                         # {jazzy, humble}
   export CPU_ARCH=amd64                           # {amd64, arm64}
   export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

   # container route: defines the wros helper
   source ~/workspaces/movensys_ws/src/wmx-r2/docker/wros.bash

   # native route: source ROS and the workspace directly
   # source /opt/ros/$ROS_DISTRO/setup.bash
   # source ~/workspaces/movensys_ws/install/setup.bash

Apply the changes:

.. code-block:: bash

   xhost +local:docker
   source ~/.bashrc

``wros`` runs a command inside ``wmx_r2_container`` as **root**, with ROS and
the workspace already sourced. Root is required: the manipulator and
differential launches need real-time scheduling. Called with no arguments it
opens an interactive shell.


Clone the repository
--------------------

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

Build and start the container
-----------------------------

Skip this section if you are building natively.

.. code-block:: bash

   cd ~/workspaces/movensys_ws/src/wmx-r2/docker
   docker compose -f general.yaml -f wmx_r2.${CPU_ARCH}.yaml down
   docker compose -f general.yaml -f wmx_r2.${CPU_ARCH}.yaml build
   docker compose -f general.yaml -f wmx_r2.${CPU_ARCH}.yaml up -d

Follow the startup logs, then open a shell:

.. code-block:: bash

   docker logs wmx_r2_container -f
   wros

.. note::

   The container and image names and the host paths — ``WMX_R2_PACKAGES``,
   ``WMX3_SDK_PATH`` — come from ``docker/.env``, relative to the ``docker/``
   directory. Edit that file if your layout differs from the default
   ``~/workspaces`` one.

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


Build the workspace
-------------------

**Rosdep update**

.. code-block:: bash

   sudo rosdep init   # only needed once per system
   rosdep update
   cd ~/workspaces/movensys_ws
   rosdep install --from-paths src --ignore-src -y

**Build** (``wmx_r2_package`` depends on ``wmx_r2_message``, so build the
message package first):

.. tab-set::

   .. tab-item:: Container
      :sync: container

      .. code-block:: bash

         # Stage 1: build the message package first
         wros colcon build --packages-select wmx_r2_message

         # Stage 2: build all remaining packages
         wros colcon build

   .. tab-item:: Native
      :sync: native

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

   wros ros2 pkg list | grep wmx
   wros ros2 pkg executables wmx_r2_package

Expected:

.. code-block:: text

   wmx_r2_control
   wmx_r2_message
   wmx_r2_package
   wmx_r2_package differential_drive_controller
   wmx_r2_package gripper_controller
   wmx_r2_package joint_position_controller
   wmx_r2_package joint_state_broadcaster
   wmx_r2_package joint_trajectory_controller
   wmx_r2_package wmx_core_motion_node
   wmx_r2_package wmx_engine_node
   wmx_r2_package wmx_ethercat_node
   wmx_r2_package wmx_io_node
   wmx_r2_package wmx_lifecycle_manager_node

Launch a robot
--------------

One launch file serves every robot of a kind. The robot is selected by the
files you pass, not by the launch file name.

.. code-block:: bash

   # low-level axis / I/O / EtherCAT control, no robot model
   wros ros2 launch wmx_r2_package wmx_r2_general_nodes.launch.py \
       use_sim_time:=false \
       'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/config/wmx_r2_general_nodes_config.yaml' \
       'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/config/wmx_parameters.xml'

   # a manipulator (Dobot CR3A shown)
   wros ros2 launch wmx_r2_package wmx_r2_manipulator.launch.py \
       use_sim_time:=false \
       'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/cr3a_manipulator_config.yaml' \
       'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/cr3a_wmx_parameters.xml' \
       use_gripper:=true

   # a differential-drive base
   wros ros2 launch wmx_r2_package wmx_r2_differential.launch.py \
       use_sim_time:=false \
       'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/diffbot_differential_config.yaml' \
       'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/diffbot_wmx_parameters.xml'

Next steps
----------

- :doc:`../examples/testing_wmx_r2` — move an axis, read an I/O bit, and read
  the EtherCAT bus, step by step
- :doc:`../api_reference/wmx_r2_package` — every launch argument and parameter
- :doc:`../commissioning/index` — **required** before moving a physical robot
