Example Applications
====================

This section provides complete examples that you can run from start to finish
on the WMX ROS2 stack. The **manipulator scenarios** come from the
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

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Manipulator scenarios

   isaacsim_setup
   movensys_manipulator_setup
   trajectory_planning
   apriltag_pick_and_place
   obstacle_avoidance
   yolo_pick_and_place
   apriltag_obstacle_avoidance

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Intelligence

   robopoly_game

Common Requirements
-------------------

- The core WMX ROS2 packages built and the WMX Runtime at ``/opt/wmx3/``
  (see :doc:`../getting_started/index`)
- Docker with ``docker compose`` (the examples run inside containers)
- An NVIDIA GPU and Isaac ROS prerequisites for the ``isaac-ros_*`` images
- EtherCAT hardware for HIL and Real modes
- The `movensys-simulation <https://github.com/movensys/movensys-simulation>`_
  repo for the Isaac Sim scenes

Before running any manipulator scenario, set up the stack once — see
:doc:`movensys_manipulator_setup`.

Supported Configurations
------------------------

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
   * - Robopoly game
     - ✓
     - ✓
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
   * - Robopoly game
     - ✓
     -

Development Roadmap
-------------------

The examples are under active development. Planned and in-progress work is
tracked below.

.. list-table::
   :header-rows: 1
   :widths: 33 33 34

   * - 2026 Q1
     - 2026 Q2
     - 2026 Q3
   * - - Add WMX3 general node
       - Add trajectory example
       - Add Apriltag example
       - Add movensys_isaac_manipulator
       - Add movensys_intel_manipulator
       - Add movensys_thor_manipulator
       - Add robotic_isaac_sim
       - Add Apriltag example

     - - Support arm64/amd64
       - Suport ROS2 humble/jazzy
       - Support dobot cr3a/cr5a
       - Add Joint Trajectory Controller node
       - Add Gripper Controller node
       - Add movensys-manipulator
       - Add movensys-simulation
       - Add movensys-intelligence
       - Add Apriltag + Obstacle avoidance example
       - Add Robopoly example
       - Delete robotic_isaac_sim
       - Delete movensys_isaac_manipulator
       - Delete movensys_intel_manipulator
       - Delete movensys_thor_manipulator
       
     - - Add Differential node
       - Add movensys-navigation
       - Add Isaac GR00T
       - Add Diffbot in isaacsim
       - Add differential drive controller node
       - Add robot option node
       - ros2_control integration
