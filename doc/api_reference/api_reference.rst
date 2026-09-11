API Reference
=============

Complete reference for the ROS2 interfaces of the WMX R2 packages.

Three packages make up WMX R2:

.. list-table::
   :header-rows: 1
   :widths: 24 76

   * - Package
     - Contents
   * - :doc:`wmx_r2_message`
     - One message (``AxesStatus``) and 22 services. Interfaces only — no
       nodes, and no dependency on the WMX3 SDK.
   * - :doc:`wmx_r2_package`
     - The ten nodes that talk to the WMX3 SDK, three launch files, and the
       per-robot example configurations.
   * - :doc:`wmx_r2_control`
     - The ``ros2_control`` hardware interface
       (``wmx_r2_control/WmxSystemHardware``), URDF xacros, controller
       YAMLs, and launch files.

How to read this section
------------------------

Two facts explain most of the interface layout.

**Commands are services; only streamed data is a topic.** Servo power, axis
configuration, homing, manual motion, I/O, and EtherCAT diagnostics are all
request/response. The topics carry feedback out and trajectory or velocity
streams in, nothing else. Multi-waypoint trajectories are the one action.

**Most nodes are lifecycle nodes, and their interfaces exist only while they
are** ``active``. ``wmx_lifecycle_manager_node`` brings them up when the
engine starts communicating and takes them down when it stops. If
``ros2 topic list`` or ``ros2 service list`` looks empty, check the node
states before anything else:

.. code-block:: bash

   ros2 service call /wmx/lifecycle/get_node_states wmx_r2_message/srv/GetNodeStates "{}"

.. note:: **There is a second, non-ROS 2 way into the same engine.**

   The WMX Runtime ships a browser UI — WOS, NetConfigurator, and MotionScope
   — that sets and tests axis parameters, servo power, homing, jogging, and
   I/O directly. It is the fastest way to tell an engine problem from a WMX R2
   problem, and it is where the ENI file is generated. See
   :doc:`../try_your_robot/wmx_web_tools`.

   Below the ROS 2 layer is the vendor SDK these nodes are built on. Its
   reference ships with the runtime at ``/opt/wmx3/Doc/Web/`` — see
   :doc:`wmx3_api`.

Interfaces by node
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 14 56

   * - Node
     - Lifecycle
     - Interfaces
   * - ``wmx_engine_node``
     - no
     - ``/wmx/engine/set_engine``, ``set_communication``,
       ``get_engine_status``, ``import_and_set_all``, ``get_axis_param``
   * - ``wmx_lifecycle_manager_node``
     - no
     - ``/wmx/lifecycle/set_node_state``, ``get_node_states``
   * - ``wmx_core_motion_node``
     - yes
     - ``/wmx/axes/*`` services; publishes ``/wmx/axes/status``
   * - ``wmx_io_node``
     - yes
     - ``/wmx/io/*`` — input and output, by bit and by byte
   * - ``wmx_ethercat_node``
     - yes
     - ``/wmx/ecat/*`` — master info, register read, scan, hot-connect
   * - ``joint_state_broadcaster``
     - yes
     - Publishes ``/joint_states`` and the simulator mirrors
   * - ``joint_trajectory_controller``
     - yes
     - ``FollowJointTrajectory`` action server
   * - ``joint_position_controller``
     - yes
     - Subscribes to the MoveIt Servo trajectory stream
   * - ``gripper_controller``
     - yes
     - ``/wmx/set_gripper``
   * - ``differential_drive_controller``
     - yes
     - ``/cmd_vel_safe`` in; ``/odom_enc``, ``/omega_enc``, ``/omega_cmd`` out

.. toctree::
   :maxdepth: 2

   communication
   ros2_services
   ros2_topics
   ros2_actions
   wmx_r2_message
   wmx_r2_package
   wmx_r2_control
   wmx3_api
