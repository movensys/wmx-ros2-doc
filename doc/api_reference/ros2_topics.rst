ROS2 Topics
============

WMX R2 keeps its topic surface small on purpose. Commands are services and
actions; topics carry only streamed data — feedback going out, and
trajectory or velocity streams coming in.

.. contents:: On this page
   :local:
   :depth: 2

Topic summary
-------------

.. list-table::
   :header-rows: 1
   :widths: 32 12 30 26

   * - Topic (default name)
     - Dir
     - Type
     - Node
   * - ``/wmx/axes/status``
     - pub
     - ``wmx_r2_message/msg/AxesStatus``
     - ``wmx_core_motion_node``
   * - ``/joint_states``
     - pub
     - ``sensor_msgs/msg/JointState``
     - ``joint_state_broadcaster``
   * - ``/isaacsim/joint_command``
     - pub
     - ``sensor_msgs/msg/JointState``
     - ``joint_state_broadcaster``
   * - ``/gazebo_position_controller/commands``
     - pub
     - ``std_msgs/msg/Float64MultiArray``
     - ``joint_state_broadcaster``
   * - ``/moveit2_trajectory/execution_active``
     - pub / sub
     - ``std_msgs/msg/Bool``
     - ``joint_trajectory_controller`` / ``joint_position_controller``
   * - ``/servo_node/delta_joint_cmds``
     - pub
     - ``control_msgs/msg/JointJog``
     - ``joint_trajectory_controller``
   * - ``/movensys_manipulator_arm_controller/joint_trajectory``
     - sub
     - ``trajectory_msgs/msg/JointTrajectory``
     - ``joint_position_controller``
   * - ``/cmd_vel_safe``
     - sub
     - ``geometry_msgs/msg/TwistStamped``
     - ``differential_drive_controller``
   * - ``/odom_enc``
     - pub
     - ``nav_msgs/msg/Odometry``
     - ``differential_drive_controller``
   * - ``/omega_enc``
     - pub
     - ``sensor_msgs/msg/JointState``
     - ``differential_drive_controller``
   * - ``/omega_cmd``
     - pub
     - ``sensor_msgs/msg/JointState``
     - ``differential_drive_controller``

.. important::

   **Every one of these names is a node parameter, not a hard-coded string.**
   The names above are the values in the shipped configuration files. They
   resolve as *absolute* names, so launching a node inside a ROS namespace
   does **not** namespace them — override the topic parameters explicitly for
   multi-robot setups.

   Topics also exist only while the owning node is ``active``: an inactive
   lifecycle node publishes and subscribes nothing.

Where the data flows
--------------------

.. mermaid::
   :caption: Manipulator topic and action flow

   flowchart LR
       MG["MoveIt2<br/>move_group"]
       SV["MoveIt Servo"]
       JTC["joint_trajectory_controller"]
       JPC["joint_position_controller"]
       JSB["joint_state_broadcaster"]
       WMX["WMX3 engine<br/>(EtherCAT)"]
       RSP["robot_state_publisher<br/>RViz, MoveIt"]
       SIM["Isaac Sim / Gazebo"]

       MG -->|"FollowJointTrajectory (action)"| JTC
       SV -->|"/…/joint_trajectory"| JPC
       JTC -->|"StartCSplinePos"| WMX
       JPC -->|"StartLinearIntplPos"| WMX
       JTC -.->|"/moveit2_trajectory/execution_active"| JPC
       JTC -.->|"/servo_node/delta_joint_cmds (zero)"| SV
       WMX -->|"encoder"| JSB
       JSB -->|"/joint_states"| RSP
       JSB -->|"/isaacsim/joint_command<br/>/gazebo_position_controller/commands"| SIM

Manipulator feedback
--------------------

/joint_states
^^^^^^^^^^^^^

Published by ``joint_state_broadcaster``. This is the topic MoveIt2,
``robot_state_publisher``, and RViz consume.

.. list-table::
   :widths: 28 72

   * - **Type**
     - ``sensor_msgs/msg/JointState``
   * - **Parameter**
     - ``encoder_joint_topic``
   * - **Rate**
     - ``joint_feedback_rate`` (Hz; ``100`` in both shipped configs)
   * - **QoS**
     - default reliable, depth 1

Content:

- ``name`` — ``joint_name`` followed by ``gripper_joint_name``
- ``position`` — the WMX ``actualPos`` of each axis, **unconverted**
- ``velocity`` — the servo's ``actualVelocity``, not a derivative of position
- ``effort`` — not filled in
- ``header.stamp`` — the node clock

.. note::

   Joint values pass through with no scaling. One axis user unit must equal
   one radian at the joint, and that is set on the WMX side in the axis
   parameter XML. There is no gear-ratio or offset parameter in any of these
   nodes. See :doc:`../commissioning/robot_parameters`.

The timer period is ``1000 / joint_feedback_rate`` truncated to whole
milliseconds, so prefer rates that divide 1000 — 100, 125, 200, 250, 500. A
value of 0 or less falls back to 100 Hz with a warning.

Gripper state comes from a single I/O **bit**, so it is two-valued: the
broadcaster reports ``gripper_close_value`` or ``gripper_open_value``, never
anything in between.

.. code-block:: bash

   ros2 topic echo /joint_states
   ros2 topic hz /joint_states      # should match joint_feedback_rate

Simulator mirrors
^^^^^^^^^^^^^^^^^

The same feedback is republished for a digital twin. Both are optional and
off when their parameter is empty.

.. list-table::
   :header-rows: 1
   :widths: 34 22 44

   * - Topic (parameter)
     - Type
     - Notes
   * - ``/isaacsim/joint_command``
       (``isaacsim_joint_topic``)
     - ``JointState``
     - Same content as ``/joint_states`` but with a **zero header stamp** —
       it is published before the stamp is filled in. Isaac consumes
       positions by name, not by time.
   * - ``/gazebo_position_controller/commands``
       (``gazebo_position_joint_topic``)
     - ``Float64MultiArray``
     - Joint **positions** only, ordered by
       ``gazebo_position_joint_axes``, gripper values appended last.
   * - (``gazebo_velocity_joint_topic``)
     - ``Float64MultiArray``
     - Joint **velocities**, ordered by ``gazebo_velocity_joint_axes``.
       Continuous joints need this, not positions.

``gazebo_position_joint_axes`` and ``gazebo_velocity_joint_axes`` list axis
numbers taken from ``joint_axes``, in the order the Gazebo controller lists
its own ``joints:``. ``gripper_joint_name`` entries come from an I/O bit
rather than an axis, so they cannot be listed there — they are appended
automatically.

/wmx/axes/status
^^^^^^^^^^^^^^^^

Published by ``wmx_core_motion_node``. This is the raw per-axis view: the
diagnostic topic, not the MoveIt one.

.. list-table::
   :widths: 28 72

   * - **Type**
     - ``wmx_r2_message/msg/AxesStatus``
   * - **Rate**
     - ``axes_status_rate`` (default ``100`` Hz)

.. code-block:: text

   std_msgs/Header header
   bool[]    amp_alarm
   bool[]    servo_on
   bool[]    home_done
   bool[]    home_switch
   bool[]    negative_ls
   bool[]    positive_ls
   bool[]    motion_complete
   float64[] pos_cmd
   float64[] velocity_cmd
   float64[] actual_pos
   float64[] actual_velocity
   float64[] actual_torque

Every array is parallel and indexed by axis. ``pos_cmd`` is what the engine
was told to do; ``actual_pos`` is what the encoder reports. The difference
between them is the following error.

.. code-block:: bash

   ros2 topic echo /wmx/axes/status --once
   ros2 topic echo /wmx/axes/status --field amp_alarm

Controller arbitration topics
-----------------------------

``joint_trajectory_controller`` (planned motion) and
``joint_position_controller`` (streamed servo motion) can command the same
axes, so they interlock over two topics.

/moveit2_trajectory/execution_active
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 28 72

   * - **Type**
     - ``std_msgs/msg/Bool``
   * - **QoS**
     - **transient_local**, depth 1 — latched, so a controller that starts
       late still sees the current value
   * - **Published by**
     - ``joint_trajectory_controller``
   * - **Subscribed by**
     - ``joint_position_controller``

``true`` for the duration of a planned goal. While it holds,
``joint_position_controller`` drops every incoming streamed trajectory.

The latch is one-directional: a servo motion already in flight is **not**
preempted when a planned goal starts. Pause MoveIt Servo, or accept that the
first goal wins the race, if both can be commanded at once.

/servo_node/delta_joint_cmds
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``control_msgs/msg/JointJog``, depth 10. On **every** goal exit path —
success, abort, or cancel — ``joint_trajectory_controller`` publishes a
zero-velocity jog for the goal's joint names, so MoveIt Servo does not
resume with a stale delta. The name is hard-coded, not a parameter.

Streamed trajectory input
-------------------------

/movensys_manipulator_arm_controller/joint_trajectory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 28 72

   * - **Type**
     - ``trajectory_msgs/msg/JointTrajectory``
   * - **Parameter**
     - ``joint_trajectory_topic``
   * - **QoS**
     - default, depth 1

The streaming path from MoveIt Servo into
``joint_position_controller``. **Only the last point of each message is
used** — this is a streaming target, not a queued trajectory.

Per axis the node computes ``velocity = |target − posCmd| / dt`` and
``acc = dec = velocity / (accel_ratio · dt)``, where ``dt`` is the point's
``time_from_start``. Because each axis gets its own velocity for a shared
``dt``, ``StartLinearIntplPos`` makes every axis arrive at the same instant.

The step is measured against the **commanded** position, not the encoder, so
following error does not feed back into the next command. Messages whose
largest per-axis step is below ``min_step`` are dropped, which keeps servo
jitter from restarting an interpolation every cycle.

Differential drive topics
-------------------------

``differential_drive_controller`` drives two EtherCAT wheel axes with
CoreMotion ``StartVel`` and exposes the Nav2 contract.

.. mermaid::
   :caption: Differential-drive data flow

   flowchart LR
       NAV["Nav2 / teleop"] -->|"/cmd_vel_safe (TwistStamped)"| DDC["differential_drive_controller"]
       DDC -->|"StartVel"| WMX["WMX3 engine"]
       WMX -->|"actualVelocity"| DDC
       DDC -->|"/odom_enc"| EKF["robot_localization EKF"]
       DDC -->|"/omega_enc, /omega_cmd"| MON["monitoring / recording"]
       EKF -->|"odom → base_link TF"| NAV

.. list-table::
   :header-rows: 1
   :widths: 24 10 26 40

   * - Topic (parameter)
     - Dir
     - Type
     - Content
   * - ``/cmd_vel_safe``
       (``cmd_vel_topic``)
     - sub
     - ``geometry_msgs/msg/TwistStamped``
     - ``twist.linear.x`` [m/s] and ``twist.angular.z`` [rad/s].
       **TwistStamped is mandatory** by message type; the header stamp is
       not read.
   * - ``/odom_enc``
       (``encoder_odometry_topic``)
     - pub
     - ``nav_msgs/msg/Odometry``
     - Pose dead-reckoned over the loop ``dt``; twist from
       ``actualVelocity``. The EKF ``odom0`` input.
   * - ``/omega_enc``
       (``encoder_omega_topic``)
     - pub
     - ``sensor_msgs/msg/JointState``
     - ``velocity = [left, right]`` wheel angular velocity [rad/s], measured.
   * - ``/omega_cmd``
       (``cmd_omega_topic``)
     - pub
     - ``sensor_msgs/msg/JointState``
     - ``velocity = [left, right]`` wheel angular velocity **command** — the
       last target sent to ``StartVel``. Monitoring only.
   * - ``/tf`` (``odom_frame`` → ``base_frame``)
     - pub
     - TF
     - Only when ``publish_tf: true``.

All four publish at ``rate`` (default 100 Hz). ``position`` and ``effort``
are left empty on both ``JointState`` topics.

.. warning::

   Keep ``publish_tf`` at its ``false`` default whenever a localization EKF
   owns the ``odom → base_link`` transform, which is the case as soon as an
   IMU is configured. Two publishers on the same TF edge produce a base that
   jumps.

.. note::

   ``cmd_vel_timeout`` (default 0.25 s) forces the wheel target to zero if
   no command arrives in that window. Freshness is measured against
   **arrival** time on this node's clock. The stop decelerates over
   ``dec_time``, so it is not an emergency stop.

   Both loop timers are wall timers, but the odometry ``dt`` comes from the
   ROS clock. A paused ``/clock`` under ``use_sim_time`` freezes the pose and
   also disables the stale-command stop.

Checking topics at runtime
--------------------------

.. code-block:: bash

   ros2 topic list                       # only active nodes appear
   ros2 topic info /joint_states -v      # publishers, subscribers, QoS
   ros2 topic hz /joint_states           # confirm the feedback rate
   ros2 topic echo /wmx/axes/status --once

If a topic is missing, check the node's lifecycle state before anything
else:

.. code-block:: bash

   ros2 service call /wmx/lifecycle/get_node_states wmx_r2_message/srv/GetNodeStates "{}"

See also
--------

- :doc:`ros2_services` -- engine, lifecycle, axis, I/O, and EtherCAT services
- :doc:`ros2_actions` -- the ``FollowJointTrajectory`` action
- :doc:`wmx_r2_message` -- ``AxesStatus`` and the service definitions
- :doc:`../integration/nav2_integration` -- how the differential topics wire into Nav2
