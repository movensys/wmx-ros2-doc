movensys-manipulator Setup
==========================

Set up the ``movensys-manipulator`` stack once before running any of the
manipulator scenarios. The examples run inside a Docker container; the host only
needs the environment variables, network tuning, and the cloned repository
described below.

1. Host environment
-------------------

Add the following to your ``~/.bashrc``, then source it. The variables select
the ROS distro, the build flavor, the CPU architecture, and the robot model.
The last line sources ``docker/mros.bash``, which defines the ``mros`` helper
used to run commands inside the container.

.. code-block:: bash

   export ROS_DOMAIN_ID=73                         # use any number
   export ROS_DISTRO=jazzy                         # {jazzy, humble}
   export CPU_ARCH=amd64                           # {amd64, arm64}
   export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

   export MOVENSYS_ROS_VERSION=isaac-ros_4.1       # {general, intel-xpu, isaac-ros_4.1, isaac-ros_3.2}
   export MANIPULATOR_MODEL=dobot_cr3a             # {dobot_cr3a, dobot_cr5a}

   source ~/workspaces/movensys_ws/src/movensys-manipulator/docker/mros.bash

.. note::

   The host paths the compose files need — ``MOVENSYS_MANIPULATOR_PACKAGES``,
   ``ISAAC_ROS_WS``, the container and image names — come from
   ``docker/.env``, relative to the ``docker/`` directory. Do not export them
   in ``~/.bashrc``; edit ``docker/.env`` if your layout differs from the
   default ``~/workspaces`` one.

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

   cd ~/workspaces/movensys_ws/src/movensys-manipulator/docker
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

For HIL and Real modes, the manipulator is brought up with WMX R2 — see
`wmx-r2/doc/launch_manipulator.md
<https://github.com/movensys/wmx-r2/blob/main/doc/launch_manipulator.md>`_,
:doc:`../api_reference/wmx_r2_package`, and
:doc:`../getting_started/install_wmx3`. One launch file serves every
manipulator; the robot is selected by the ``config_file`` and
``wmx_param_file`` you pass.

.. note:: **Isaac Sim scenes**

   The Simulation and HIL modes load USD scenes in NVIDIA Isaac Sim. See
   :doc:`isaacsim_setup` for the Isaac Sim installation and the scene layout.
