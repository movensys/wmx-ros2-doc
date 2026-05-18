WMX ROS2 Documentation
=======================

Overview
----------------------------------------

Welcome to the WMX ROS2 documentation. Between ROS2 trajectory planners
(MoveIt2, Nav2) and industrial servo drives sits a layer most motion stacks
leave empty: deterministic, scan-rate command execution. Existing
``ros2_control`` hardware interfaces either talk TCP/IP to a closed controller,
or expose raw EtherCAT cyclic access without motion profile generation. This
project provides the missing layer.

What is wmx-ros2
----------------------------------------

wmx-ros2 is an MIT-licensed ROS2 package that handles trajectory interpolation,
multi-axis coordination, and scan-rate EtherCAT command generation in a
single-PC architecture. It exposes two modes: a ``ros2_control``
``SystemInterface`` plugin for use with standard controllers
(``JointTrajectoryController``, ``DiffDriveController``), and a native execution
mode that bypasses the per-cycle ``ros2_control`` loop for latency-critical
workloads. It runs in simulation, hardware-in-loop, and real EtherCAT
deployment on x86 and Jetson under PREEMPT_RT.

What is WMX
----------------------------------------

WMX is the deterministic motion control engine that wmx-ros2 sits on top of.
It has over a decade of industrial deployment in semiconductor, manufacturing,
and precision robotics, and uses EtherCAT under a real-time kernel as the
fieldbus. It supports motion profiling such as PVT (Position-Velocity-Time)
and multi-axis coordinated motion -- it takes irregular trajectory waypoints
and generates exact cyclic commands at the scan rate. WMX is available as a
free, full-featured download with a renewable time-limited license.




Key capabilities
----------------------------------------

- Follow the :doc:`getting_started/index` guide to set up your environment and get running.
- Explore :doc:`integration/integration` for current and future integration scenarios.
- Check the :doc:`api_reference/api_reference` for ROS2 services, topics, and actions.
- Scan through :doc:`support` for answers to common issues. 







.. toctree::
   :maxdepth: 3

   getting_started/index
   integration/integration
   api_reference/api_reference
   support
   about