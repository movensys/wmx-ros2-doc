movensys-manipulator Setup
==========================

Set up the ``movensys-manipulator`` stack once before running any of the
manipulator scenarios. The examples run inside a Docker container; the host only
needs the environment variables, network tuning, and the cloned repository
described below.

1. Host environment
-------------------

Add the following to your ``~/.bashrc`` (source it afterwards). The variables
select the ROS distro, the build flavor, the CPU architecture, and the robot
model, and define the ``mros`` helper used to run commands inside the container.

.. code-block:: bash

   export ROS_DOMAIN_ID=73                         # use any number
   export ROS_DISTRO=jazzy                         # {jazzy, humble}
   export MOVENSYS_ROS_VERSION=isaac-ros_4.1       # {isaac-ros_4.1, isaac-ros_3.2, general}
   export CPU_ARCH=amd64                           # {amd64, arm64}
   export MANIPULATOR_MODEL=dobot_cr3a             # {dobot_cr3a, dobot_cr5a}

   export HOST_USER_UID=$(id -u)
   export HOST_USER_GID=$(id -g)
   export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

   export MOVENSYS_MANIPULATOR_PACKAGES=~/workspaces/movensys_ws/src/movensys-manipulator
   export ISAAC_ROS_WS=~/workspaces/isaac_ros-dev

   mros() {
     if [ $# -eq 0 ]; then
       docker exec -it -u admin movensys_manipulator_container \
         bash -lc 'source /opt/ros/${ROS_DISTRO}/setup.bash && source /home/admin/workspaces/movensys_ws/install/setup.bash && exec bash -i'
     else
       docker exec -it -u admin movensys_manipulator_container \
         bash -lc "source /opt/ros/\${ROS_DISTRO}/setup.bash && source /home/admin/workspaces/movensys_ws/install/setup.bash && $*"
     fi
   }

Allow the container to reach the host X server and reload the shell:

.. code-block:: bash

   xhost +local:docker
   source ~/.bashrc

2. CycloneDDS network buffers
-----------------------------

Raise the kernel socket-buffer limits so the CycloneDDS RMW can carry the
joint-state and image traffic without drops:

.. code-block:: bash

   sudo tee /etc/sysctl.d/99-network-buffers.conf << 'EOF'
   net.core.rmem_max=67108864
   net.core.rmem_default=67108864
   net.core.wmem_max=67108864
   net.core.wmem_default=67108864
   EOF

   sudo sysctl -p /etc/sysctl.d/99-network-buffers.conf
   sysctl net.core.rmem_max net.core.rmem_default net.core.wmem_max net.core.wmem_default

3. Clone the repository
-----------------------

.. code-block:: bash

   mkdir -p ~/workspaces/movensys_ws/src
   cd ~/workspaces/movensys_ws/src
   git clone git@github.com:movensys/movensys-manipulator.git

4. Build and start the container
--------------------------------

.. note::

   For the ``isaac-ros_*`` build flavors, complete the
   `Isaac ROS getting-started setup
   <https://nvidia-isaac-ros.github.io/getting_started/index.html>`_ first
   (the ``release-3.2`` and ``release-4.1`` guides match
   ``MOVENSYS_ROS_VERSION=isaac-ros_3.2`` / ``isaac-ros_4.1``).

The compose files combine the ROS-version layer with the per-architecture
manipulator layer:

.. code-block:: bash

   cd ${MOVENSYS_MANIPULATOR_PACKAGES}/docker
   docker compose -f ${MOVENSYS_ROS_VERSION}.yaml -f movensys_manipulator.${CPU_ARCH}.yaml down
   docker compose -f ${MOVENSYS_ROS_VERSION}.yaml -f movensys_manipulator.${CPU_ARCH}.yaml build
   docker compose -f ${MOVENSYS_ROS_VERSION}.yaml -f movensys_manipulator.${CPU_ARCH}.yaml up -d

Follow the container startup logs:

.. code-block:: bash

   docker logs movensys_manipulator_container -f

5. Enter the container
----------------------

All scenario commands run through ``mros``, which executes inside the
``movensys_manipulator_container``. Open an interactive shell:

.. code-block:: bash

   mros

Verify the build by launching the robot description in RViz:

.. code-block:: bash

   mros ros2 launch movensys_manipulator_description movensys_manipulator_rviz.launch.py

For HIL and Real modes, the manipulator is brought up with WMX ROS2 (see
``wmx-ros2/doc/launch_<MANIPULATOR_MODEL>_manipulator.md`` and
:doc:`../getting_started/testing_wmx_ros2`).

.. note:: **Isaac Sim scenes**

   The Simulation and HIL modes load USD scenes in NVIDIA Isaac Sim. See
   :doc:`isaacsim_setup` for the Isaac Sim installation and the scene layout.
