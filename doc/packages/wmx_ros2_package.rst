wmx_ros2_package
=================

Overview
--------

The ``wmx_ros2_package`` is the main application package of the WMX ROS2
system. It contains all executable nodes, launch files, and configuration
files for driving robots — such as the Dobot CR3A and CR5A manipulators —
through the WMX motion control engine over EtherCAT.

The package provides two groups of nodes:

- **General nodes** -- ``wmx_engine_node``, ``wmx_core_motion_node``,
  ``wmx_io_node``, and ``wmx_ethercat_node`` expose the WMX engine, axis,
  I/O, and EtherCAT interfaces as ROS2 services and topics. They are
  robot-agnostic.
- **Manipulator controllers** -- ``joint_state_broadcaster``,
  ``joint_trajectory_controller``, and ``gripper_controller`` add joint-state
  feedback, MoveIt2 trajectory execution, and gripper control for a specific
  robot, configured from a per-robot YAML file.

**Package Metadata:**

.. list-table::
   :widths: 25 75

   * - **Package Name**
     - ``wmx_ros2_package``
   * - **Version**
     - 0.1.0
   * - **License**
     - MIT
   * - **Build Type**
     - ``ament_cmake``
   * - **C++ Standard**
     - C++17

Package Structure
-----------------

.. code-block:: text

   wmx_ros2_package/
   ├── CMakeLists.txt
   ├── package.xml
   ├── include/
   │   ├── wmx_engine_node.hpp               # WmxEngineNode class definition
   │   ├── wmx_core_motion_node.hpp          # WmxCoreMotionNode class definition
   │   ├── wmx_io_node.hpp                   # WmxIoNode class definition
   │   └── wmx_ethercat_node.hpp             # WmxEtherCatNode class definition
   ├── src/
   │   ├── wmx_engine_node.cpp               # Engine lifecycle node
   │   ├── wmx_core_motion_node.cpp          # Axis control + parameter node
   │   ├── wmx_io_node.cpp                   # Digital I/O node
   │   ├── wmx_ethercat_node.cpp             # EtherCAT diagnostics node
   │   ├── joint_state_broadcaster.cpp       # Joint state publisher node
   │   ├── joint_trajectory_controller.cpp   # FollowJointTrajectory action node
   │   └── gripper_controller.cpp            # Gripper control node
   ├── launch/
   │   ├── wmx_ros2_general_nodes.launch.py
   │   ├── wmx_ros2_cr3a_manipulator.launch.py
   │   └── wmx_ros2_cr5a_manipulator.launch.py
   ├── config/
   │   ├── cr3a_manipulator_config.yaml
   │   ├── cr3a_wmx_parameters.xml           # WMX3 axis params for CR3A
   │   ├── cr5a_manipulator_config.yaml
   │   ├── cr5a_wmx_parameters.xml           # WMX3 axis params for CR5A
   │   └── diffbot_wmx_parameters.xml        # WMX3 axis params for a diff-drive base
   └── test/

Dependencies
------------

Package Dependencies (package.xml)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - Dependency
     - Type
     - Purpose
   * - ``ament_cmake``
     - buildtool
     - CMake build system
   * - ``rclcpp``
     - depend
     - ROS2 C++ client library
   * - ``rclcpp_action``
     - depend
     - Action server support (FollowJointTrajectory)
   * - ``std_srvs``
     - depend
     - Standard service types (``SetBool``, ``Trigger``)
   * - ``std_msgs``
     - depend
     - Standard message types (``Bool``, ``Float64MultiArray``)
   * - ``sensor_msgs``
     - depend
     - ``JointState`` messages
   * - ``control_msgs``
     - depend
     - ``FollowJointTrajectory`` action type
   * - ``trajectory_msgs``
     - depend
     - ``JointTrajectory`` messages
   * - ``wmx_ros2_message``
     - depend
     - Custom message and service definitions
   * - ``ros2launch``
     - exec
     - Launch system
   * - ``joint_state_publisher``
     - exec
     - Joint state publishing utilities
   * - ``robot_state_publisher``
     - exec
     - Robot TF broadcasting
   * - ``rviz2``
     - exec
     - Visualization
   * - ``xacro``
     - exec
     - URDF preprocessing

CMake Dependencies (find_package)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``ament_cmake``, ``rclcpp``, ``rclcpp_action``, ``std_msgs``, ``std_srvs``,
``sensor_msgs``, ``control_msgs``, ``trajectory_msgs``, and
``wmx_ros2_message``.

WMX Libraries (External)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Executables link against the WMX shared libraries at ``/opt/wmx3/lib/``.
Each node links only the libraries it needs:

.. list-table::
   :header-rows: 1
   :widths: 32 40 28

   * - Library
     - Executable(s)
     - Purpose
   * - ``libwmx3api.so`` / ``libimdll.so``
     - All nodes
     - Core WMX device/engine management (and internal dependency)
   * - ``libcoremotionapi.so``
     - ``wmx_core_motion_node``, ``joint_state_broadcaster``,
       ``joint_trajectory_controller``, ``gripper_controller``
     - Position, velocity, and axis control
   * - ``libadvancedmotionapi.so``
     - ``joint_trajectory_controller``
     - Cubic spline trajectory execution
   * - ``libioapi.so``
     - ``wmx_io_node``, ``joint_state_broadcaster``, ``gripper_controller``
     - Digital I/O (gripper control)
   * - ``libecapi.so``
     - ``wmx_engine_node``, ``wmx_ethercat_node``
     - EtherCAT network scan and diagnostics

Node Coordination
-----------------

Nodes start up in a fixed order, coordinated by two ``ready`` heartbeat
topics so that dependent nodes only activate once the engine and motion
layers are live:

.. mermaid::
   :caption: Node startup coordination via ready signals

   sequenceDiagram
       participant E as wmx_engine_node
       participant C as wmx_core_motion_node
       participant I as wmx_io_node / wmx_ethercat_node
       participant M as manipulator controllers

       E->>E: CreateDevice + StartCommunication
       E-->>C: /wmx/engine/ready (Bool)
       E-->>I: /wmx/engine/ready (Bool)
       E-->>M: /wmx/engine/ready (Bool)
       C-->>M: /wmx/core_motion/ready (Bool)
       Note over M: joint_state_broadcaster waits on<br/>/wmx/core_motion/ready before publishing

- ``wmx_engine_node`` creates the WMX device, starts EtherCAT communication,
  and publishes ``/wmx/engine/ready``.
- ``wmx_core_motion_node``, ``wmx_io_node``, ``wmx_ethercat_node``,
  ``gripper_controller``, and ``joint_trajectory_controller`` wait for
  ``/wmx/engine/ready`` before activating.
- ``wmx_core_motion_node`` publishes ``/wmx/core_motion/ready``;
  ``joint_state_broadcaster`` waits for it before loading parameters and
  publishing joint feedback.

General Nodes
-------------

wmx_engine_node
^^^^^^^^^^^^^^^^^

Manages the WMX device lifecycle: creates the device, starts/stops EtherCAT
communication, and publishes a ready signal to coordinate dependent nodes.
On startup it automatically calls ``CreateDevice`` and ``StartCommunication``,
and also exposes manual-override services.

**Source:** ``src/wmx_engine_node.cpp`` — **Node name:** ``wmx_engine_node``

.. list-table:: Services
   :header-rows: 1
   :widths: 35 35 30

   * - Service
     - Type
     - Description
   * - ``/wmx/engine/set_device``
     - ``wmx_ros2_message/srv/SetEngine``
     - Create or close the WMX device handle
   * - ``/wmx/engine/set_comm``
     - ``std_srvs/srv/SetBool``
     - Start or stop EtherCAT communication
   * - ``/wmx/engine/get_status``
     - ``std_srvs/srv/Trigger``
     - Query engine state (Idle/Running/Communicating/Shutdown)
   * - ``/wmx/engine/scan_network``
     - ``std_srvs/srv/Trigger``
     - Trigger EtherCAT network scan to discover slaves

Publishes ``/wmx/engine/ready`` (``std_msgs/msg/Bool``) — ``true`` when
communication is active, ``false`` on shutdown.

wmx_core_motion_node
^^^^^^^^^^^^^^^^^^^^^^

Provides service-based axis control, XML parameter load/get, topic-based
motion commands, and per-axis state publishing. Waits for
``/wmx/engine/ready`` before activating.

**Source:** ``src/wmx_core_motion_node.cpp`` — **Node name:** ``wmx_core_motion_node``

.. list-table:: Services
   :header-rows: 1
   :widths: 35 35 30

   * - Service
     - Type
     - Description
   * - ``/wmx/axis/set_on``
     - ``wmx_ros2_message/srv/SetAxis``
     - Enable/disable servo drives
   * - ``/wmx/axis/clear_alarm``
     - ``wmx_ros2_message/srv/SetAxis``
     - Clear amplifier faults
   * - ``/wmx/axis/set_mode``
     - ``wmx_ros2_message/srv/SetAxis``
     - Set position (0) or velocity (1) mode
   * - ``/wmx/axis/set_polarity``
     - ``wmx_ros2_message/srv/SetAxis``
     - Set rotation direction (1 or -1)
   * - ``/wmx/axis/set_gear_ratio``
     - ``wmx_ros2_message/srv/SetAxisGearRatio``
     - Configure encoder gear ratio
   * - ``/wmx/axis/homing``
     - ``wmx_ros2_message/srv/SetAxis``
     - Set current position as home (zero)
   * - ``/wmx/params/load``
     - ``wmx_ros2_message/srv/LoadWmxParams``
     - Load axis parameters from a WMX3 XML file
   * - ``/wmx/params/get``
     - ``wmx_ros2_message/srv/GetWmxParams``
     - Retrieve active axis parameters as text

**Published topic:** ``/wmx/axis/state`` (``wmx_ros2_message/msg/AxisState``,
100 Hz) — full per-axis status.

**Subscribed topics:** ``/wmx/axis/velocity`` (``AxisVelocity`` →
``CoreMotion::StartVel()``), ``/wmx/axis/position`` (``AxisPose`` →
``CoreMotion::StartPos()``), ``/wmx/axis/position/relative`` (``AxisPose`` →
``CoreMotion::StartMov()``). Also publishes ``/wmx/core_motion/ready``.

wmx_io_node
^^^^^^^^^^^^^

Service-based access to EtherCAT digital I/O. Waits for ``/wmx/engine/ready``.

**Source:** ``src/wmx_io_node.cpp`` — **Node name:** ``wmx_io_node``

.. list-table:: Services
   :header-rows: 1
   :widths: 35 35 30

   * - Service
     - Type
     - Description
   * - ``/wmx/io/get_input_bit``
     - ``wmx_ros2_message/srv/GetIoBit``
     - Read a single digital input bit
   * - ``/wmx/io/get_output_bit``
     - ``wmx_ros2_message/srv/GetIoBit``
     - Read back a digital output bit
   * - ``/wmx/io/get_input_bytes``
     - ``wmx_ros2_message/srv/GetIoBytes``
     - Read a block of digital input bytes
   * - ``/wmx/io/get_output_bytes``
     - ``wmx_ros2_message/srv/GetIoBytes``
     - Read a block of digital output bytes
   * - ``/wmx/io/set_output_bit``
     - ``wmx_ros2_message/srv/SetIoBit``
     - Write a single digital output bit
   * - ``/wmx/io/set_output_bytes``
     - ``wmx_ros2_message/srv/SetIoBytes``
     - Write a block of digital output bytes

wmx_ethercat_node
^^^^^^^^^^^^^^^^^^^

EtherCAT diagnostic services for network monitoring and debugging. Waits for
``/wmx/engine/ready``.

**Source:** ``src/wmx_ethercat_node.cpp`` — **Node name:** ``wmx_ethercat_node``

.. list-table:: Services
   :header-rows: 1
   :widths: 35 40 25

   * - Service
     - Type
     - Description
   * - ``/wmx/ecat/get_network_state``
     - ``wmx_ros2_message/srv/EcatGetNetworkState``
     - Full network state: master + all slaves
   * - ``/wmx/ecat/register_read``
     - ``wmx_ros2_message/srv/EcatRegisterRead``
     - Read raw EtherCAT register from a slave
   * - ``/wmx/ecat/reset_statistics``
     - ``wmx_ros2_message/srv/EcatResetStatistics``
     - Reset packet loss / timing counters
   * - ``/wmx/ecat/start_hotconnect``
     - ``wmx_ros2_message/srv/EcatStartHotconnect``
     - Initiate hot-connect for dynamic slave addition

Manipulator Controllers
-----------------------

joint_state_broadcaster
^^^^^^^^^^^^^^^^^^^^^^^^^

Loads the robot's WMX axis parameters and publishes encoder feedback as
``JointState`` (plus simulator mirrors). Waits for ``/wmx/core_motion/ready``
before publishing.

**Source:** ``src/joint_state_broadcaster.cpp`` — **Node name:** ``joint_state_broadcaster``

.. list-table:: Parameters
   :header-rows: 1
   :widths: 32 16 52

   * - Parameter
     - Type
     - Description
   * - ``joint_axes``
     - ``int[]``
     - WMX axis indices for the robot joints (e.g. ``[0,1,2,3,4,5]``)
   * - ``joint_feedback_rate``
     - ``int``
     - Encoder publish rate in Hz
   * - ``gripper_open_value`` / ``gripper_close_value``
     - ``double``
     - Joint position reported when the gripper is open / closed
   * - ``joint_name``
     - ``string[]``
     - Joint names for the JointState message
   * - ``gripper_joint_name``
     - ``string[]``
     - Gripper finger joint names (e.g. ``picker_1_joint``, ``picker_2_joint``)
   * - ``gripper_address``
     - ``int[]``
     - I/O ``[byte, bit]`` address read for gripper state
   * - ``encoder_joint_topic``
     - ``string``
     - Primary joint state topic (typically ``/joint_states``)
   * - ``isaacsim_joint_topic``
     - ``string``
     - Isaac Sim joint command topic
   * - ``gazebo_joint_topic``
     - ``string``
     - Gazebo position controller topic
   * - ``wmx_param_file_path``
     - ``string``
     - Absolute path to the WMX axis parameter XML (resolved at launch)

.. list-table:: Published Topics
   :header-rows: 1
   :widths: 35 35 30

   * - Topic (param)
     - Message Type
     - Description
   * - ``encoder_joint_topic``
     - ``sensor_msgs/msg/JointState``
     - Joint positions + gripper state
   * - ``isaacsim_joint_topic``
     - ``sensor_msgs/msg/JointState``
     - Mirror for Isaac Sim
   * - ``gazebo_joint_topic``
     - ``std_msgs/msg/Float64MultiArray``
     - Joint positions for Gazebo

joint_trajectory_controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Action server that executes MoveIt2-planned trajectories on the robot using
WMX cubic spline interpolation. Waits for ``/wmx/engine/ready``.

**Source:** ``src/joint_trajectory_controller.cpp`` — **Node name:** ``joint_trajectory_controller``

.. list-table:: Parameters
   :header-rows: 1
   :widths: 32 16 52

   * - Parameter
     - Type
     - Description
   * - ``joint_axes``
     - ``int[]``
     - WMX axis indices (sets the spline ``dimensionCount``)
   * - ``joint_trajectory_action``
     - ``string``
     - Action server name for ``FollowJointTrajectory``

Hosts the ``FollowJointTrajectory`` action
(``control_msgs/action/FollowJointTrajectory``). See
:doc:`../api_reference/ros2_actions` for the full execution details.

gripper_controller
^^^^^^^^^^^^^^^^^^^^

Controls the pneumatic gripper via EtherCAT digital I/O. Waits for
``/wmx/engine/ready``.

**Source:** ``src/gripper_controller.cpp`` — **Node name:** ``gripper_controller``

.. list-table:: Parameters
   :header-rows: 1
   :widths: 32 16 52

   * - Parameter
     - Type
     - Description
   * - ``wmx_gripper_topic``
     - ``string``
     - Service name for gripper open/close (typically ``/wmx/set_gripper``)
   * - ``gripper_address``
     - ``int[]``
     - I/O ``[byte, bit]`` address written to actuate the gripper

The gripper service is a ``std_srvs/srv/SetBool`` (``true`` = close,
``false`` = open) backed by ``Io::SetOutBit``.

Launch Files
------------

wmx_ros2_general_nodes.launch.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starts the four general nodes for standalone axis/IO/EtherCAT control without
manipulator controllers.

**Nodes launched:** ``wmx_engine_node``, ``wmx_core_motion_node``,
``wmx_io_node``, ``wmx_ethercat_node``.

**Arguments:** ``use_sim_time`` (default ``false``). **Config:** none.

.. code-block:: bash

   ros2 launch wmx_ros2_package wmx_ros2_general_nodes.launch.py

wmx_ros2_cr3a_manipulator.launch.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Full Dobot CR3A manipulator launch. Includes
``wmx_ros2_general_nodes.launch.py`` and then starts the manipulator
controllers.

**Nodes launched:** the four general nodes (via include), plus
``joint_state_broadcaster``, ``joint_trajectory_controller``, and
``gripper_controller``.

**Arguments:** ``use_sim_time`` (default ``false``).
**Config:** ``config/cr3a_manipulator_config.yaml`` and
``config/cr3a_wmx_parameters.xml`` (the WMX parameter path is resolved at
launch time).

.. code-block:: bash

   ros2 launch wmx_ros2_package wmx_ros2_cr3a_manipulator.launch.py \
     use_sim_time:=false

wmx_ros2_cr5a_manipulator.launch.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Full Dobot CR5A manipulator launch. Includes the general nodes and starts
``joint_state_broadcaster`` and ``joint_trajectory_controller``.

**Arguments:** ``use_sim_time`` (default ``false``).
**Config:** ``config/cr5a_manipulator_config.yaml`` and
``config/cr5a_wmx_parameters.xml``.

.. code-block:: bash

   ros2 launch wmx_ros2_package wmx_ros2_cr5a_manipulator.launch.py \
     use_sim_time:=false

.. note::

   The launch commands above assume the workspace is already sourced. On real
   hardware the nodes require ``sudo`` with the ROS2 environment preserved —
   see :doc:`../getting_started/testing_wmx_ros2` for the full ``sudo
   --preserve-env`` invocation.

Configuration Files
-------------------

cr3a_manipulator_config.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parameters for the Dobot CR3A manipulator, shared by the three manipulator
controllers:

.. code-block:: yaml

   joint_state_broadcaster:
     ros__parameters:
       joint_feedback_rate: 100
       gripper_open_value: 0.00
       gripper_close_value: 0.045
       joint_axes: [0, 1, 2, 3, 4, 5]
       joint_name: ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6"]
       gripper_joint_name: ["picker_1_joint", "picker_2_joint"]
       gripper_address: [0, 0]
       encoder_joint_topic: /joint_states
       isaacsim_joint_topic: /isaacsim/joint_command
       gazebo_joint_topic: /gazebo_position_controller/commands
       wmx_param_file_path: ""   # resolved at launch via get_package_share_directory

   joint_trajectory_controller:
     ros__parameters:
       joint_axes: [0, 1, 2, 3, 4, 5]
       joint_trajectory_action: /movensys_manipulator_arm_controller/follow_joint_trajectory

   gripper_controller:
     ros__parameters:
       wmx_gripper_topic: /wmx/set_gripper
       gripper_address: [0, 0]

cr5a_manipulator_config.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The CR5A equivalent of the CR3A config, used by the CR5A launch file. It
configures ``joint_state_broadcaster`` and ``joint_trajectory_controller`` for
the CR5A robot.

WMX Parameter XML Files
^^^^^^^^^^^^^^^^^^^^^^^^^^

Robot-specific WMX parameter files define per-axis motor configuration (gear
ratios, polarities, limits, home positions):

- ``cr3a_wmx_parameters.xml`` -- Dobot CR3A manipulator (6 joints)
- ``cr5a_wmx_parameters.xml`` -- Dobot CR5A manipulator (6 joints)
- ``diffbot_wmx_parameters.xml`` -- differential-drive base axes

These files are loaded at runtime via
``CoreMotion::config->ImportAndSetAll(path)``.

Building the Package
--------------------

This package depends on ``wmx_ros2_message`` and must be built after it:

.. code-block:: bash

   cd ~/workspaces/movensys_ws

   # Stage 1: Build message package
   colcon build --packages-select wmx_ros2_message
   source install/setup.bash

   # Stage 2: Build application package
   colcon build --packages-select wmx_ros2_package
   source install/setup.bash

Verify executables are available:

.. code-block:: bash

   ros2 pkg executables wmx_ros2_package

Expected:

.. code-block:: text

   wmx_ros2_package gripper_controller
   wmx_ros2_package joint_state_broadcaster
   wmx_ros2_package joint_trajectory_controller
   wmx_ros2_package wmx_core_motion_node
   wmx_ros2_package wmx_engine_node
   wmx_ros2_package wmx_ethercat_node
   wmx_ros2_package wmx_io_node
