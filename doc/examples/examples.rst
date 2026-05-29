Example Applications
====================

.. rubric:: Overview

This section contains complete application examples showing how to use the
WMX ROS2 packages with different frameworks and hardware setups. Each example
is a **standalone workspace** that depends on the core ``wmx_ros2_message``
and ``wmx_ros2_package`` packages.

These examples demonstrate the **robot-agnostic design** of the system -- the
same WMX ROS2 nodes and interfaces are used regardless of the specific robot
model or compute platform. Only the configuration files (YAML parameters,
WMX XML parameters, and launch files) differ between setups.

.. list-table:: Example Summary
   :header-rows: 1
   :widths: 30 30 40

   * - Example
     - Platform
     - Description
   * - :doc:`isaac_manipulator`
     - NVIDIA Jetson Orin
     - Manipulator control with Isaac Sim integration
   * - :doc:`intel_manipulator`
     - Intel x86_64
     - Manipulator control with Gazebo integration

.. rubric:: Requirements

All examples require:

- The core WMX ROS2 packages built and sourced
  (see :doc:`../getting_started/index`)
- LMX(WMX Runtime) installed at ``/opt/wmx3/``
- EtherCAT hardware connected (for physical robot operation)

Each example page describes any additional dependencies specific to that setup.

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

**Future development:**

.. toctree::
   :maxdepth: 2

   isaac_manipulator
   intel_manipulator
