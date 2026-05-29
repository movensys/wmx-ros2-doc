API Reference
=============

Complete reference for all ROS2 interfaces exposed by the WMX ROS2 packages.
The interfaces are provided by the general nodes in ``wmx_ros2_package`` —
``wmx_engine_node``, ``wmx_core_motion_node``, ``wmx_ethercat_node``, and
``wmx_io_node`` — together with the manipulator controllers
(joint state broadcaster, gripper controller, and joint trajectory
controller). All custom message and service types are defined in
``wmx_ros2_message``.

**ROS2 Services** documents the request/response interfaces:

- **Engine management** (``wmx_engine_node``) -- device creation/teardown
  (``/wmx/engine/set_device``), communication start/stop
  (``/wmx/engine/set_comm``), status query (``/wmx/engine/get_status``), and
  EtherCAT network scan (``/wmx/engine/scan_network``).
- **Axis control** (``wmx_core_motion_node``) -- servo on/off, clear alarm,
  set command mode, set polarity, set gear ratio, and homing
  (``/wmx/axis/*``), plus loading and reading axis parameters from XML
  (``/wmx/params/load``, ``/wmx/params/get``).
- **I/O** (``wmx_io_node``) -- read and write digital input/output bits and
  bytes (``/wmx/io/*``). Gripper open/close (``/wmx/set_gripper``) is layered
  on top of digital output bit 0.
- **EtherCAT** (``wmx_ethercat_node``) -- network state, register read,
  statistics reset, and hot-connect (``/wmx/ecat/*``).

**ROS2 Topics** covers the streamed data: ``/joint_states`` for MoveIt2 and
RViz feedback (rate set by ``joint_feedback_rate``, plus Isaac Sim and Gazebo
variants), ``/wmx/axis/state`` for detailed per-axis status (``AxisState`` at
100 Hz), the motion-command inputs ``/wmx/axis/position``,
``/wmx/axis/position/relative`` and ``/wmx/axis/velocity``, and the per-node
``ready`` heartbeats.

**ROS2 Actions** describes the ``FollowJointTrajectory`` action server that
receives multi-waypoint trajectories from MoveIt2 and executes them on the
robot via WMX spline interpolation.

.. toctree::
   :maxdepth: 2

   communication
   wmx_ros2_message
   wmx_ros2_package
   ros2_services
   ros2_topics
   ros2_actions
