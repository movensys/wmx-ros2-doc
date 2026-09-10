Example Applications
====================

This section provides complete examples that you can run from start to finish
on the WMX R2 stack. The **manipulator scenarios** come from the
`movensys-manipulator <https://github.com/movensys/movensys-manipulator>`_
repository (manipulator with MoveIt2 / Isaac cuMotion planning and
Nvblox / YOLO / AprilTag perception). The **navigation scenarios** come from the
`movensys-navigation <https://github.com/movensys/movensys-navigation>`_
repository (a differential-drive base with Nav2 planning, EKF odometry, and SLAM
mapping). The **Robopoly game** is a voice-driven VLM/LLM application from the
`movensys-intelligence <https://github.com/movensys/movensys-intelligence>`_
repository, built on top of the manipulator stack.

Every manipulator and navigation scenario runs in three execution modes. The
difference between them is *where the motion actually happens*:

.. mermaid::
   :caption: Each mode makes one more layer real

   flowchart LR
       S["<b>Simulation</b><br/>planner and simulator physics"]
       H["<b>HIL</b><br/>plus the real WMX engine"]
       R["<b>Real</b><br/>plus the physical servos"]
       S -->|"the engine becomes real"| H -->|"the motors become real"| R

.. list-table::
   :header-rows: 1
   :widths: 14 20 22 22 22

   * - Mode
     - Planner
     - WMX engine
     - EtherCAT
     - Motion
   * - **Simulation**
     - real
     - not used
     - not used
     - simulated physics
   * - **HIL**
     - real
     - **real**
     - simulated platform
     - simulated, driven by the engine
   * - **Real**
     - real
     - **real**
     - **real bus**
     - **physical servos**

HIL is the step that catches configuration errors: the engine, the axis
parameters, the gear ratios, and the whole WMX R2 node graph are exactly what
the real robot will use — only the motors are not. An axis that moves the
wrong way in HIL would have moved the wrong way on the robot.

The mode is selected in ``/opt/wmx3/Module.ini`` (simulation platform versus
EtherCAT platform) and by which USD scene you open. See
:doc:`testing_wmx_r2` for the ``Module.ini`` switch.

.. warning:: **Run the modes in order Simulation, then HIL, then Real.**

   The three modes are a safety sequence, not a convenience. Incorrect gear
   ratios, encoder resolution, joint directions, or home offsets cause
   unexpected motion even when the software is working correctly, and
   Simulation and HIL are where those errors are cheap to find.

   Before the **Real** tab of any scenario, complete
   :doc:`../commissioning/index`: verify the robot parameters
   (:doc:`../commissioning/robot_parameters`), run the low-speed single-axis
   procedure (:doc:`../commissioning/first_motion`), and put the separate
   safety measures in :doc:`../commissioning/safety` in place. Check
   :doc:`../commissioning/validated_hardware` for what has actually been
   validated on your robot.

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Application stacks

   testing_wmx_r2
   isaacsim_setup
   movensys_manipulator
   movensys_navigation

Common Requirements
-------------------

- The core WMX R2 packages built and the WMX Runtime at ``/opt/wmx3/``
  (see :doc:`../getting_started/index`)
- Docker with ``docker compose`` (the examples run inside containers)
- An NVIDIA GPU and Isaac ROS prerequisites for the ``isaac-ros_*`` images
- EtherCAT hardware for HIL and Real modes
- The `movensys-simulation <https://github.com/movensys/movensys-simulation>`_
  repo for the Isaac Sim scenes

Before running any scenario, set up the stack once — see
:doc:`movensys_manipulator_setup` for manipulator scenarios and
:doc:`movensys_navigation_setup` for navigation scenarios.

Development Roadmap
-------------------

The examples are under active development. Planned and in-progress work is
tracked below.

.. note::

   This roadmap covers example applications and platform support only. It is
   not a commitment to provide safety functionality equivalent to a certified
   industrial robot controller. Planned safety-related material — recommended
   safety architectures, STO and safety-PLC integration examples, and
   commissioning guidance — is listed separately in
   :doc:`../commissioning/safety`.

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
       - Support ROS2 humble/jazzy
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
       
     - - Add movensys-navigation
       - Add Diffbot in isaacsim
       - Add differential drive controller node
       - ros2_control integration
       - Support Jetson Development Kit 
       - Universal NIC Kernel driver
       - Free license for 6 hours
