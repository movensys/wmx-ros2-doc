Example Applications
====================

Runnable, end-to-end examples that build on the WMX ROS2 stack. The
**manipulator scenarios** come from the
`movensys-manipulator <https://github.com/movensys/movensys-manipulator>`_
repository (Dobot CR3A / CR5A arms with MoveIt2 / Isaac cuMotion planning and
Nvblox / YOLO / AprilTag perception). The **Robopoly game** is a voice-driven
VLM/LLM application from the
`movensys-intelligence <https://github.com/movensys/movensys-intelligence>`_
repository, built on top of the manipulator stack.

Every manipulator scenario runs in three execution modes:

- **Simulation** -- pure simulation (Isaac Sim or Gazebo), no hardware
- **HIL** -- hardware-in-the-loop: simulator visuals with the real WMX runtime
- **Real** -- the real robot via WMX over EtherCAT

.. rubric:: Common requirements

- The core WMX ROS2 packages built and the LMX (WMX Runtime) at ``/opt/wmx3/``
  (see :doc:`../getting_started/index`)
- Docker with ``docker compose`` (the examples run inside containers)
- An NVIDIA GPU and Isaac ROS prerequisites for the ``isaac-ros_*`` images
- EtherCAT hardware for HIL and Real modes
- The `movensys-simulation <https://github.com/movensys/movensys-simulation>`_
  repo for the Isaac Sim scenes

.. rubric:: Manipulator setup

Clone ``movensys-manipulator`` and configure the host environment, then build
and start the container and enter it with the ``mros`` helper (host setup is in
``doc/1_setup.md``, container setup in ``doc/2_docker.md``). Key environment
variables:

.. code-block:: bash

   export ROS_DISTRO=jazzy                    # {jazzy, humble}
   export MANIPULATOR_MODEL=dobot_cr3a        # {dobot_cr3a, dobot_cr5a}
   export MOVENSYS_ROS_VERSION=isaac-ros_4.1  # {isaac-ros_4.1, isaac-ros_3.2, general}
   export CPU_ARCH=amd64                       # {amd64, arm64}

All scenario commands run through ``mros``, which executes inside the
``movensys_manipulator_container``. Isaac Sim scenes load from
``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/<scenario>.usd``. For
HIL and Real modes, the manipulator is brought up with WMX ROS2 (see
``wmx-ros2/doc/launch_<MANIPULATOR_MODEL>_manipulator.md`` and
:doc:`../getting_started/testing_wmx_ros2`).

.. note:: **Isaac Sim scenes**

   The ready-to-open USD scenes come from the
   `movensys-simulation <https://github.com/movensys/movensys-simulation>`_
   repository, organized under ``dobot_cr3a/`` and ``dobot_cr5a/``. Scenes are
   named ``<n><mode>_<example>.usd`` where the mode suffix is ``a`` =
   simulation, ``b`` = HIL, ``c`` = real. Running them requires NVIDIA Isaac
   Sim 5.0.0+ with the ``isaacsim.ros2.bridge`` extension enabled. See the
   repository README for the full Isaac Sim setup.

.. rubric:: Supported Configurations

**Framework support:**

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Demo Scenario
     - ROS2 Humble
     - ROS2 Jazzy
     - Isaac ROS 3.2
     - Isaac ROS 4.1
   * - Joint trajectory motion
     - ✓
     - ✓
     - ✓
     - ✓
   * - AprilTag pick and place
     - ✓
     - ✓
     - ✓
     - ✓
   * - Obstacle avoidance
     -
     -
     - ✓
     - ✓
   * - AprilTag pick and place with obstacle avoidance
     -
     -
     - ✓
     - ✓

**Robot platform support:**

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Demo Scenario
     - Dobot CR3A
     - Dobot CR5A
   * - Joint trajectory motion
     - ✓
     - ✓
   * - AprilTag pick and place
     - ✓
     -
   * - Obstacle avoidance
     - ✓
     -
   * - AprilTag pick and place with obstacle avoidance
     - ✓
     -

.. toctree::
   :maxdepth: 1
   :caption: Manipulator scenarios

   trajectory_planning
   apriltag_pick_and_place
   obstacle_avoidance
   yolo_pick_and_place
   apriltag_obstacle_avoidance

.. toctree::
   :maxdepth: 1
   :caption: Intelligence

   robopoly_game
