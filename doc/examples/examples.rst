Example Applications
====================

This section provides complete examples that you can run from start to finish
on the WMX R2 stack. They draw on four repositories:

.. list-table::
   :header-rows: 1
   :widths: 18 28 44 10

   * - Part
     - Repository
     - What it contains
     - Helper
   * - **Manipulator**
     - `movensys-manipulator <https://github.com/movensys/movensys-manipulator>`_
     - Manipulator with MoveIt2 / Isaac cuMotion planning and
       Nvblox / YOLO / AprilTag perception
     - ``mros``
   * - **Navigation**
     - `movensys-navigation <https://github.com/movensys/movensys-navigation>`_
     - A differential-drive base with Nav2 planning, EKF odometry, and SLAM
       mapping
     - ``nros``
   * - **Robopoly game**
     - `movensys-intelligence <https://github.com/movensys/movensys-intelligence>`_
     - A voice-driven VLM/LLM application built on top of the manipulator stack
     - ``mros``
   * - **Isaac Sim scenes**
     - `movensys-simulation <https://github.com/movensys/movensys-simulation>`_
     - The USD scenes used by the manipulator and navigation scenarios
     - —

Each stack runs in its own Docker container, and the **Helper** column names
the shell helper that runs a command inside it (``wros`` does the same for the
core WMX R2 container — see :doc:`testing_wmx_r2`). Isaac Sim runs on the host.

.. note:: **The robots in these scenarios are examples.**

   The scenarios run on the Dobot CR3A and CR5A arms and the ``diffbot``
   differential-drive base because those are the models this project ships a
   ready-made parameter file, URDF, and planning configuration for. WMX R2
   itself controls axes, not a specific robot model: it commands EtherCAT
   servo drives over CoE and drives any EtherCAT robot or machine regardless
   of brand.

   Running your own machine means supplying its configuration — see
   :doc:`../try_your_robot/robot_parameters` — and
   :doc:`../try_your_robot/validated_hardware` for what has been validated so
   far. :doc:`testing_wmx_r2` needs no robot model at all; it exercises the
   axes directly.

Every scenario is presented in three modes:

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
   :doc:`../try_your_robot/index`: verify the robot parameters
   (:doc:`../try_your_robot/robot_parameters`), run the low-speed single-axis
   procedure (:doc:`../try_your_robot/first_motion`), and put the separate
   safety measures in :doc:`../try_your_robot/safety` in place. Check
   :doc:`../try_your_robot/validated_hardware` for what has actually been
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
   :doc:`../try_your_robot/safety`.

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
