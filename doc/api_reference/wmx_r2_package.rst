wmx_r2_package
=================

Overview
--------

``wmx_r2_package`` is where WMX R2 actually runs. It holds the ten nodes
that talk to the WMX3 SDK, the three launch files that start them, and the
per-robot example configurations.

Two rules shape the whole package:

**No robot is baked into any launch file.** Every launch file takes its
paths as arguments — ``config_file`` and ``wmx_param_file``, plus
``urdf_file`` and ``controllers_file`` on the ``ros2_control`` variants — so
one launch file serves every robot of that kind. Moving to a different robot
changes the files you pass, not the code.

**Every node except the engine and the lifecycle manager is a managed
(lifecycle) node.** They start ``unconfigured`` and attach to the WMX device
only at ``configure``. Their ROS interfaces are created at ``activate`` and
destroyed at ``deactivate``, so an inactive node advertises nothing.

.. mermaid::
   :caption: wmx_r2_package node layout

   flowchart TB
       subgraph GEN["wmx_r2_general_nodes.launch.py"]
           ENG["wmx_engine_node<br/><i>owns the engine</i>"]
           LCM["wmx_lifecycle_manager_node<br/><i>drives every managed node</i>"]
           CM["wmx_core_motion_node<br/><i>lifecycle</i>"]
           IO["wmx_io_node<br/><i>lifecycle</i>"]
           EC["wmx_ethercat_node<br/><i>lifecycle</i>"]
       end

       subgraph MAN["+ wmx_r2_manipulator.launch.py"]
           JSB["joint_state_broadcaster"]
           JTC["joint_trajectory_controller"]
           JPC["joint_position_controller"]
           GC["gripper_controller<br/><i>use_gripper:=true</i>"]
       end

       subgraph DIF["+ wmx_r2_differential.launch.py"]
           JSB2["joint_state_broadcaster"]
           DDC["differential_drive_controller"]
       end

       ENG -->|engine status| LCM
       LCM -->|configure / activate| CM & IO & EC
       LCM -->|configure / activate| JSB & JTC & JPC & GC
       LCM -->|configure / activate| JSB2 & DDC
       SDK["WMX3 SDK  /opt/wmx3"]
       ENG --> SDK
       CM --> SDK
       IO --> SDK
       EC --> SDK
       JSB --> SDK
       JTC --> SDK
       JPC --> SDK
       DDC --> SDK

Package structure
-----------------

.. code-block:: text

   wmx_r2_package/
   ├── src/
   │   ├── wmx_engine_node.cpp                # engine + device
   │   ├── wmx_lifecycle_manager_node.cpp     # lifecycle supervisor
   │   ├── wmx_core_motion_node.cpp           # axes services + status
   │   ├── wmx_io_node.cpp                    # digital I/O
   │   ├── wmx_ethercat_node.cpp              # EtherCAT master
   │   ├── joint_state_broadcaster.cpp        # encoder feedback
   │   ├── joint_trajectory_controller.cpp    # FollowJointTrajectory
   │   ├── joint_position_controller.cpp      # MoveIt Servo stream
   │   ├── gripper_controller.cpp             # gripper output bit
   │   └── differential_drive_controller.cpp  # diff-drive + odometry
   ├── include/                               # one header per node
   ├── launch/
   │   ├── wmx_r2_general_nodes.launch.py
   │   ├── wmx_r2_manipulator.launch.py
   │   └── wmx_r2_differential.launch.py
   ├── config/
   │   ├── wmx_r2_general_nodes_config.yaml   # generic, no robot
   │   └── wmx_parameters.xml
   ├── example/
   │   ├── cr3a_manipulator_config.yaml
   │   ├── cr3a_wmx_parameters.xml
   │   ├── cr5a_manipulator_config.yaml
   │   ├── cr5a_wmx_parameters.xml
   │   ├── diffbot_differential_config.yaml
   │   └── diffbot_wmx_parameters.xml
   ├── test/                                  # launch tests, no hardware needed
   ├── CMakeLists.txt
   └── package.xml

Dependencies
------------

Package dependencies (``package.xml``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: xml

   <depend>rclcpp</depend>
   <depend>rclcpp_action</depend>
   <depend>rclcpp_lifecycle</depend>
   <depend>lifecycle_msgs</depend>
   <depend>std_srvs</depend>
   <depend>std_msgs</depend>
   <depend>sensor_msgs</depend>
   <depend>control_msgs</depend>
   <depend>trajectory_msgs</depend>
   <depend>geometry_msgs</depend>
   <depend>nav_msgs</depend>
   <depend>tf2</depend>
   <depend>tf2_ros</depend>
   <depend>wmx_r2_message</depend>

   <exec_depend>ros2launch</exec_depend>
   <exec_depend>joint_state_publisher</exec_depend>
   <exec_depend>robot_state_publisher</exec_depend>
   <exec_depend>rviz2</exec_depend>
   <exec_depend>xacro</exec_depend>

WMX libraries (external)
^^^^^^^^^^^^^^^^^^^^^^^^

The package compiles against the WMX3 SDK at the CMake cache path
``WMX3_SDK_PATH``, default ``/opt/wmx3``. The same path is compiled in and
passed to ``CreateDevice`` at runtime by every node.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Library
     - Used for
   * - ``libwmx3api``
     - Device create/close, engine and communication control
   * - ``libcoremotionapi``
     - Axis status, servo power, position/velocity/jog motion
   * - ``libadvancedmotionapi``
     - C-spline trajectory execution (``joint_trajectory_controller`` only)
   * - ``libioapi``
     - Digital input and output
   * - ``libecapi``
     - EtherCAT master and slave diagnostics

.. important::

   At **runtime** the dynamic linker must find the SDK's shared libraries
   (``libimdll.so`` and friends): either an ``ld.so.conf.d`` entry for
   ``/opt/wmx3/lib`` — the SDK installer's default — or
   ``LD_LIBRARY_PATH=/opt/wmx3/lib``. This matters in containers that only
   mount the SDK.

   Manipulator and differential launches need **root** for real-time
   scheduling. Start them with ``sudo --preserve-env`` on the host, or with
   ``wros`` in the container.

Node coordination
-----------------

``wmx_engine_node`` owns the WMX3 engine and nothing else.
``wmx_lifecycle_manager_node`` watches it and drives every other node.

While the engine is communicating, every managed node found on the graph is
brought up to ``active``; a node that joins late or respawns is picked up on
a later sweep. When the engine stops or its device is closed, all of them are
deactivated and cleaned back to ``unconfigured``, because their device
handles are dead, and brought up again when the engine returns.

This is not limited to WMX nodes. Any managed node in the same namespace — a
lifecycle ``joint_state_publisher``, a Nav2 node, one of your own — is driven
the same way. Order it with the manager's ``managed_nodes`` parameter, or
drive nodes by hand through ``/wmx/lifecycle/set_node_state``.

.. mermaid::
   :caption: What each lifecycle state means for a WMX node

   stateDiagram-v2
       direction LR
       [*] --> unconfigured : process starts

       unconfigured --> inactive : configure
       inactive --> unconfigured : cleanup
       inactive --> active : activate
       active --> inactive : deactivate
       unconfigured --> [*] : shutdown

       note left of unconfigured
           No WMX device.
           No ROS interfaces.
       end note

       note right of inactive
           WMX device attached
           (CreateDevice done).
           Still no ROS interfaces.
       end note

       note right of active
           Publishers, subscriptions,
           services, action servers
           and timers exist.
           This is the only state
           that answers.
       end note

.. list-table:: What drives the transitions
   :header-rows: 1
   :widths: 30 70

   * - Trigger
     - Effect
   * - Engine reaches ``Communicating``
     - The manager brings every managed node up to ``active``, in
       ``managed_nodes`` order
   * - Engine stops, or its device closes
     - Every node is deactivated and cleaned back to ``unconfigured`` — their
       device handles are dead
   * - A node joins late or respawns
     - Picked up on the next discovery sweep and brought up
   * - ``set_node_state`` / ``ros2 lifecycle set``
     - Manual override for one node, or for all of them with an empty
       ``node_name``

.. important::

   Two consequences worth remembering:

   - **A configured-but-inactive node advertises nothing.** An empty
     ``ros2 service list`` is a state problem far more often than a crash.
   - **Deactivating** ``joint_state_broadcaster`` **switches the servos off**,
     which drops an arm's holding torque. It is the only node in the stack
     that touches servo power.

General nodes
-------------

wmx_engine_node
^^^^^^^^^^^^^^^

Creates the WMX3 device, starts and stops EtherCAT communication, reports the
engine state, and imports the WMX parameter XML. It is an ordinary node, not
a lifecycle node — it is what the lifecycle manager follows.

.. list-table::
   :header-rows: 1
   :widths: 27 15 58

   * - Parameter
     - Default
     - Meaning
   * - ``core``
     - ``-1``
     - CPU core for the real-time engine (``-1`` = SDK default)
   * - ``affinity_mask``
     - ``0``
     - CPU affinity bitmask (``0`` = SDK default)
   * - ``wmx_param_file_path``
     - ``""``
     - XML imported right after the device is created; injected by launch
       from the ``wmx_param_file`` argument

Services: ``/wmx/engine/set_engine``, ``set_communication``,
``get_engine_status``, ``import_and_set_all``, ``get_axis_param``.

wmx_lifecycle_manager_node
^^^^^^^^^^^^^^^^^^^^^^^^^^

Polls ``/wmx/engine/get_engine_status`` every ``discovery_period`` seconds
and drives every managed node to match.

.. list-table::
   :header-rows: 1
   :widths: 27 15 58

   * - Parameter
     - Default
     - Meaning
   * - ``managed_nodes``
     - ``[]``
     - Bring-up order; take-down is the reverse
   * - ``discovery_period``
     - ``2.0``
     - Seconds between engine-state sweeps

Services: ``/wmx/lifecycle/set_node_state``,
``/wmx/lifecycle/get_node_states``.

wmx_core_motion_node
^^^^^^^^^^^^^^^^^^^^

*Lifecycle.* Serves all ``/wmx/axes/*`` services and publishes
``/wmx/axes/status``. It also arbitrates: while any node listed in
``motion_controllers`` is ``active``, the manual motion services answer
``success: false``. See :doc:`ros2_services`.

wmx_io_node
^^^^^^^^^^^

*Lifecycle.* Serves all ``/wmx/io/*`` services — input and output, by bit
and by byte, scalar and scattered.

wmx_ethercat_node
^^^^^^^^^^^^^^^^^

*Lifecycle.* Serves all ``/wmx/ecat/*`` services — master info, register
read, statistics reset, network scan, hot-connect.

Manipulator controllers
-----------------------

Four lifecycle nodes on top of the general nodes. Each attaches to the WMX3
device itself and calls CoreMotion / AdvancedMotion / IO directly — the
general nodes own the engine, not the motion these controllers command.

joint_state_broadcaster
^^^^^^^^^^^^^^^^^^^^^^^

Reads the encoder every cycle and publishes ``/joint_states``, plus the
optional Isaac Sim and Gazebo mirrors.

It is also **the only node in the stack that touches servo power.** At
``activate`` it calls ``/wmx/axes/clear_amp_alarm`` then
``/wmx/axes/set_servo_on`` for every ``joint_axes`` entry, retrying up to
five times before failing the transition. At ``deactivate`` it switches the
servos **off** — so deactivating the broadcaster drops the arm's holding
torque.

.. list-table::
   :header-rows: 1
   :widths: 32 18 50

   * - Parameter
     - Default
     - Meaning
   * - ``joint_axes``
     - ``[]``
     - WMX3 axis index per joint
   * - ``joint_name``
     - ``[j1..j6]``
     - Joint names published in ``JointState.name``
   * - ``joint_feedback_rate``
     - ``0``
     - Publish rate in Hz; ``0`` falls back to 100 with a warning. Prefer
       rates that divide 1000.
   * - ``encoder_joint_topic``
     - ``/encoder_joint_topic/no_param``
     - Real-robot feedback topic; deployments set ``/joint_states``
   * - ``isaacsim_joint_topic``
     - ``/isaacsim_joint_topic/no_param``
     - Isaac Sim mirror, published with a zero header stamp
   * - ``gazebo_position_joint_topic``
     - ``""``
     - ``Float64MultiArray`` of positions; empty disables the publisher
   * - ``gazebo_position_joint_axes``
     - ``[]``
     - Axis order for that topic
   * - ``gazebo_velocity_joint_topic``
     - ``""``
     - ``Float64MultiArray`` of velocities, for continuous joints
   * - ``gazebo_velocity_joint_axes``
     - ``[]``
     - Axis order for that topic
   * - ``gripper_joint_name``
     - ``[]``
     - Extra joint names appended to the feedback message
   * - ``gripper_address``
     - ``[0, 0]``
     - ``[byte, bit]`` of the output bit read back for gripper state
   * - ``gripper_open_value``
     - ``0.0``
     - Reported joint value while the bit is 0
   * - ``gripper_close_value``
     - ``0.0``
     - Reported joint value while the bit is 1

joint_trajectory_controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Serves ``FollowJointTrajectory`` and executes it as a WMX3 time-based
C-spline. See :doc:`ros2_actions` for the full execution contract.

.. list-table::
   :header-rows: 1
   :widths: 32 18 50

   * - Parameter
     - Default
     - Meaning
   * - ``joint_axes``
     - ``[]``
     - WMX3 axis index per trajectory joint
   * - ``joint_name``
     - ``[]``
     - Joint name per axis; goal columns are matched by name
   * - ``joint_trajectory_action``
     - ``/joint_trajectory_action/no_param``
     - Action server name; must equal the controller name in MoveIt2

joint_position_controller
^^^^^^^^^^^^^^^^^^^^^^^^^

Follows MoveIt Servo's streamed ``JointTrajectory`` using WMX3 linear
interpolation, so every axis arrives at the same instant. Only the last point
of each message is used.

.. list-table::
   :header-rows: 1
   :widths: 32 18 50

   * - Parameter
     - Default
     - Meaning
   * - ``joint_axes``
     - ``[]``
     - WMX3 axis index per joint
   * - ``joint_name``
     - ``[j1..j6]``
     - Name-to-axis map for incoming ``joint_names``
   * - ``joint_trajectory_topic``
     - ``/joint_trajectory_topic/no_param``
     - Streamed trajectory input from MoveIt Servo
   * - ``default_velocity``
     - ``0.1``
     - Velocity used when ``time_from_start`` is 0; deployments use ``0.5``
   * - ``accel_ratio``
     - ``0.5``
     - Fraction of the step spent accelerating; deployments use ``0.3``
   * - ``min_step``
     - ``0.1``
     - Deadband against the *commanded* position; deployments use ``0.001``

gripper_controller
^^^^^^^^^^^^^^^^^^

Serves ``/wmx/set_gripper`` (``std_srvs/SetBool``) and drives one WMX output
bit. Started only with ``use_gripper:=true``.

.. list-table::
   :header-rows: 1
   :widths: 32 18 50

   * - Parameter
     - Default
     - Meaning
   * - ``wmx_gripper_topic``
     - ``/wmx_gripper_topic/no_param``
     - Service name (the parameter is called "topic" for historical reasons)
   * - ``gripper_address``
     - ``[0, 0]``
     - ``[byte, bit]`` of the output bit driven by the service
   * - ``pre_setup_io``
     - ``false``
     - Run the gripper power-up sequence at ``configure``. The addresses are
       compiled in — leave it ``false`` unless your gripper matches them.

.. note::

   The defaults here are deliberate non-values. Topic and action names
   default to ``/<name>/no_param`` and the axis lists default to empty, so an
   unconfigured node is loud and inert rather than silently wrong. Every
   deployment supplies a YAML.

   All parameters are read **once at node construction**. There is no
   parameter-set callback: ``ros2 param set`` is accepted by rclcpp but
   changes nothing. Edit the YAML and restart.

Differential drive controller
-----------------------------

differential_drive_controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*Lifecycle.* Drives two EtherCAT wheel axes with CoreMotion ``StartVel`` and
exposes the autonomy contract: ``/cmd_vel_safe`` in, ``/odom_enc`` and the
wheel-velocity topics out. See :doc:`ros2_topics`.

.. list-table::
   :header-rows: 1
   :widths: 28 16 56

   * - Parameter
     - Default
     - Meaning
   * - ``left_axis`` / ``right_axis``
     - ``0`` / ``1``
     - WMX3 axis index of each drive wheel
   * - ``wheel_radius``
     - ``0.095``
     - Drive-wheel radius in m; must be > 0
   * - ``wheel_to_wheel``
     - ``0.55``
     - Wheel separation in m; must be > 0
   * - ``rate``
     - ``100``
     - Control-loop rate in Hz; one loop does one ``GetStatus``
   * - ``acc_time`` / ``dec_time``
     - ``1.0``
     - ``StartVel`` ramp times in **milliseconds**
   * - ``cmd_vel_timeout``
     - ``0.25``
     - Seconds without a command before the wheel target is forced to zero
   * - ``publish_tf``
     - ``false``
     - Publish ``odom → base_link``. Keep false when an EKF owns that TF.
   * - ``odom_frame`` / ``base_frame``
     - ``odom`` / ``base_link``
     - Frame ids for ``/odom_enc`` and the optional TF
   * - ``joint_name``
     - ``[left, right]``
     - Wheel joint names, in ``[left, right]`` order; needs exactly 2

Launch files
------------

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Launch file
     - Starts
   * - ``wmx_r2_general_nodes.launch.py``
     - ``wmx_engine_node``, ``wmx_lifecycle_manager_node``,
       ``wmx_core_motion_node``, ``wmx_io_node``, ``wmx_ethercat_node``
   * - ``wmx_r2_manipulator.launch.py``
     - the general nodes, plus ``joint_state_broadcaster``,
       ``joint_trajectory_controller``, ``joint_position_controller``, and
       ``gripper_controller`` when ``use_gripper:=true``
   * - ``wmx_r2_differential.launch.py``
     - the general nodes, plus ``joint_state_broadcaster`` and
       ``differential_drive_controller``

The ``ros2_control`` variants live in the ``wmx_r2_control`` package; see
:doc:`../integration/moveit2_integration` and
:doc:`../integration/nav2_integration`.

wmx_r2_general_nodes.launch.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 24 16 60

   * - Argument
     - Default
     - Description
   * - ``use_sim_time``
     - ``false``
     - Use the simulation clock
   * - ``config_file``
     - ``""``
     - YAML with the general node parameters. Empty loads no parameter file:
       launch warns and every node falls back to its compiled defaults.
   * - ``wmx_param_file``
     - ``""``
     - WMX3 parameter XML imported at engine start. Empty imports nothing.

.. code-block:: bash

   wros ros2 launch wmx_r2_package wmx_r2_general_nodes.launch.py \
       use_sim_time:=false \
       'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/config/wmx_r2_general_nodes_config.yaml' \
       'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/config/wmx_parameters.xml'

wmx_r2_manipulator.launch.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 24 16 60

   * - Argument
     - Default
     - Description
   * - ``use_sim_time``
     - ``false``
     - Use the simulation clock
   * - ``config_file``
     - **required**
     - YAML with the manipulator node parameters
   * - ``wmx_param_file``
     - ``""``
     - WMX3 parameter XML imported at engine start
   * - ``use_gripper``
     - ``false``
     - Start ``gripper_controller``

The manipulator launch passes ``config_file`` down to the general-nodes
launch unchanged, so engine core and affinity, the WMX parameter path, and
the bring-up order all live in that one YAML.

.. code-block:: bash

   # Dobot CR3A
   wros ros2 launch wmx_r2_package wmx_r2_manipulator.launch.py \
       use_sim_time:=false \
       'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/cr3a_manipulator_config.yaml' \
       'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/cr3a_wmx_parameters.xml' \
       use_gripper:=true

   # Dobot CR5A
   wros ros2 launch wmx_r2_package wmx_r2_manipulator.launch.py \
       use_sim_time:=false \
       'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/cr5a_manipulator_config.yaml' \
       'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/cr5a_wmx_parameters.xml'

wmx_r2_differential.launch.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Same three arguments as the general-nodes launch, with ``config_file``
required.

.. code-block:: bash

   wros ros2 launch wmx_r2_package wmx_r2_differential.launch.py \
       use_sim_time:=false \
       'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/diffbot_differential_config.yaml' \
       'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/diffbot_wmx_parameters.xml'

Configuration files
-------------------

A deployment is **one YAML plus one XML**.

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - File
     - Owns
   * - ROS parameter YAML
     - Everything on the ROS side: which axis is which joint, topic and
       action names, feedback rates, gripper wiring, bring-up order.
   * - WMX parameter XML
     - Everything on the engine side: gear ratio, feedback, soft limits,
       ``inPos`` window, home type. This is where "one axis user unit =
       1 rad at the joint" is set.

.. important::

   Joint values pass through the ROS nodes **unconverted**. There is no
   gear-ratio or offset parameter anywhere in ``wmx_r2_package``. If the
   robot moves the wrong distance, the XML is wrong — not the YAML. See
   :doc:`../commissioning/robot_parameters`.

cr3a_manipulator_config.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   joint_state_broadcaster:
     ros__parameters:
       joint_feedback_rate: 100
       joint_axes: [0, 1, 2, 3, 4, 5]
       joint_name: ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6"]
       gripper_joint_name: ["picker_1_joint", "picker_2_joint"]
       gripper_address: [0, 0]
       gripper_open_value: 0.00
       gripper_close_value: 0.045
       encoder_joint_topic: /joint_states
       isaacsim_joint_topic: /isaacsim/joint_command
       gazebo_position_joint_topic: /gazebo_position_controller/commands
       gazebo_position_joint_axes: [0, 1, 2, 3, 4, 5]

   joint_trajectory_controller:
     ros__parameters:
       joint_axes: [0, 1, 2, 3, 4, 5]
       joint_name: ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6"]
       joint_trajectory_action: /movensys_manipulator_arm_controller/follow_joint_trajectory

   joint_position_controller:
     ros__parameters:
       joint_axes: [0, 1, 2, 3, 4, 5]
       joint_name: ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6"]
       joint_trajectory_topic: /movensys_manipulator_arm_controller/joint_trajectory
       accel_ratio: 0.3
       default_velocity: 0.5
       min_step: 0.001

   gripper_controller:
     ros__parameters:
       wmx_gripper_topic: /wmx/set_gripper
       gripper_address: [0, 0]
       pre_setup_io: true

   wmx_engine_node:
     ros__parameters:
       core: -1
       affinity_mask: 0

   wmx_core_motion_node:
     ros__parameters:
       axes_status_rate: 100
       motion_controllers:
         - joint_trajectory_controller
         - joint_position_controller

   wmx_lifecycle_manager_node:
     ros__parameters:
       managed_nodes:                 # device-level nodes first
         - wmx_core_motion_node
         - wmx_io_node
         - wmx_ethercat_node
         - joint_state_broadcaster
         - joint_trajectory_controller
         - joint_position_controller
         - gripper_controller
       discovery_period: 1.0

``cr5a_manipulator_config.yaml`` is the same file with the CR5A's values.
On a gripperless arm, drop ``gripper_controller`` from ``managed_nodes`` and
leave ``use_gripper`` at ``false``.

diffbot_differential_config.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   differential_drive_controller:
     ros__parameters:
       left_axis: 0
       right_axis: 1
       rate: 100
       wheel_radius: 0.095
       wheel_to_wheel: 0.55
       cmd_vel_timeout: 0.25
       publish_tf: false
       odom_frame: odom
       base_frame: base_link
       joint_name: ["drivewheel_left_joint", "drivewheel_right_joint"]
       cmd_vel_topic: /cmd_vel_safe
       cmd_omega_topic: /omega_cmd
       encoder_odometry_topic: /odom_enc
       encoder_omega_topic: /omega_enc

   joint_state_broadcaster:
     ros__parameters:
       joint_feedback_rate: 100
       joint_axes: [0, 1]
       joint_name: ["drivewheel_left_joint", "drivewheel_right_joint"]
       encoder_joint_topic: /joint_states
       gazebo_velocity_joint_topic: /velocity_controller/commands
       gazebo_velocity_joint_axes: [0, 1]

   wmx_core_motion_node:
     ros__parameters:
       motion_controllers:
         - differential_drive_controller

   wmx_lifecycle_manager_node:
     ros__parameters:
       managed_nodes:
         - wmx_core_motion_node
         - wmx_io_node
         - wmx_ethercat_node
         - joint_state_broadcaster
         - differential_drive_controller

What to change per robot
^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Always per robot
     - ``joint_axes`` and ``joint_name`` — identical lists across the three
       motion nodes — ``joint_feedback_rate``, and the WMX parameter XML
   * - Per gripper
     - ``gripper_address``, ``gripper_open_value`` / ``gripper_close_value``,
       ``gripper_joint_name``, ``wmx_gripper_topic``, ``pre_setup_io``
   * - Per planning stack
     - ``joint_trajectory_action`` and ``joint_trajectory_topic``, which must
       match the MoveIt2 controller config and the Servo output topic
   * - Usually defaults
     - ``accel_ratio``, ``default_velocity``, ``min_step``, and the simulator
       mirror topics
   * - Never
     - The 1000-point spline buffer size, the arbitration topics, the
       clear-alarm/servo-on sequence, and any gear-ratio scaling — the WMX
       XML owns that one

Building the package
--------------------

Build the messages first, then the rest:

.. code-block:: bash

   wros colcon build --packages-select wmx_r2_message
   wros colcon build

The package builds only where the WMX3 SDK is present. ``wmx_r2_message``
does not need the SDK and can be built anywhere.

Tests under ``test/`` are launch tests and need no hardware:

.. code-block:: bash

   colcon test --packages-select wmx_r2_package

See also
--------

- :doc:`ros2_services` -- every service, with call examples
- :doc:`ros2_topics` -- every topic, with QoS and rates
- :doc:`ros2_actions` -- the ``FollowJointTrajectory`` contract
- :doc:`wmx_r2_message` -- interface definitions
- :doc:`../commissioning/robot_parameters` -- what belongs in the WMX XML
