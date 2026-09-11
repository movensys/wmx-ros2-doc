Nav2 Navigation (Mobile Base)
=============================

Overview
--------

Nav2 is the mobile-base counterpart to :doc:`moveit2_integration`. Where MoveIt2
plans arm trajectories, `Nav2 <https://docs.nav2.org/>`_ plans and follows paths
for a wheeled base. The
`movensys-navigation <https://github.com/movensys/movensys-navigation>`_
repository provides the ``movensys_navigation_nav2_config`` package, which wraps
Nav2 for a differential-drive base and executes the resulting velocity commands
on the wheels through the WMX R2 stack.

Nav2 produces a stream of velocity commands from a costmap-aware controller; WMX
turns those into wheel motion on a deterministic real-time cycle over EtherCAT.
As with the manipulator, the same configuration drives three execution modes:
pure **simulation** (Isaac Sim or Gazebo), **hardware-in-the-loop** (simulator
visuals with the real WMX runtime), and **real** base control.

Architecture
------------

.. mermaid::
   :caption: Nav2 → WMX R2 velocity and odometry loop
   :zoom:

   flowchart LR
       GOAL["Goal pose<br/>(RViz / action)"]
       NAV2["Nav2 servers<br/>planner · controller · BT"]
       SMOOTH["velocity_smoother"]
       WMX["WMX differential<br/>drive controller"]
       WHEELS["Wheel servos<br/>(EtherCAT)"]
       EKF["robot_localization<br/>EKF"]
       AMCL["AMCL<br/>(map localization)"]

       GOAL --> NAV2
       NAV2 -->|"/cmd_vel_nav"| SMOOTH
       SMOOTH -->|"/cmd_vel_safe"| WMX
       WMX --> WHEELS
       WHEELS -->|"/odom_enc"| EKF
       EKF -->|"/odom"| AMCL
       AMCL --> NAV2

The command path is one-way to the wheels and the odometry path closes the loop
back to localization:

1. Nav2's ``controller_server`` produces velocity commands on ``/cmd_vel_nav``.
2. ``velocity_smoother`` limits and republishes them on the single base input
   topic ``/cmd_vel_safe`` (manual teleop publishes here directly — see
   :doc:`../examples/manual_driving`).
3. The WMX differential-drive controller converts the ``Twist`` into
   left/right wheel velocities (from ``wheel_radius`` and ``wheel_to_wheel``)
   and commands the wheel axes with ``CoreMotion::StartVel()`` on a fixed cycle.
4. Wheel encoder feedback is dead-reckoned into ``/odom_enc``, fused by the
   ``robot_localization`` EKF into ``/odom``, and used by ``AMCL`` to localize
   against the map — which is what Nav2 plans on.

Execution modes
---------------

The WMX side drives the base in either of two ways. Both consume ``/cmd_vel_safe``
and publish the same encoder odometry, so the Nav2 side is identical either way.

.. note::

   WMX R2 runs in its own container and is launched with ``wros``; the Nav2
   stack runs in the ``movensys-navigation`` container and is launched with
   ``nros``. The two helpers are not interchangeable — ``wros`` runs as root,
   which the real-time launches require. Both containers must share the same
   ``ROS_DOMAIN_ID`` and ``RMW_IMPLEMENTATION``.

   The full launch arguments are in `wmx-r2/doc/launch_differential.md
   <https://github.com/movensys/wmx-r2/blob/main/doc/launch_differential.md>`_
   and :doc:`../api_reference/wmx_r2_package`.

.. tab-set::

   .. tab-item:: Native controller

      ``wmx_r2_package`` runs a native ``differential_drive_controller`` node
      that feeds velocity straight to the wheels, with the WMX ``StartVel``
      profile doing the acceleration and braking. This is the default used by
      the navigation examples.

      .. code-block:: bash

         wros ros2 launch wmx_r2_package wmx_r2_differential.launch.py \
             use_sim_time:=false \
             'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/diffbot_differential_config.yaml' \
             'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/diffbot_wmx_parameters.xml'

   .. tab-item:: ros2_control

      ``wmx_r2_control`` runs the standard
      ``diff_drive_controller/DiffDriveController`` on top of the
      ``WmxSystemHardware`` ``SystemInterface`` plugin. The controller is
      configured as a pure passthrough (velocity/acceleration/jerk limiters
      off) so the WMX profile still owns the timing.

      .. code-block:: bash

         wros ros2 launch wmx_r2_control wmx_r2_control_differential.launch.py \
             use_sim_time:=false \
             'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/diffbot_differential_config.yaml' \
             'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/diffbot_wmx_parameters.xml' \
             'urdf_file:=$(ros2 pkg prefix --share wmx_r2_control)/urdf/diffbot.wmx.urdf.xacro' \
             'controllers_file:=$(ros2 pkg prefix --share wmx_r2_control)/config/diffbot_controllers.yaml'

Setup
-----

The navigation stack runs inside the ``movensys-navigation`` Docker container.
Commands run through the ``nros`` container helper (the navigation counterpart
of ``mros``). Key environment variables:

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Variable
     - Purpose
   * - ``ROS_DISTRO``
     - ``humble`` or ``jazzy`` (selects the matching Nav2 params file, since
       plugin names differ per distro)
   * - ``NAVIGATION_MODEL``
     - Base model, e.g. ``diffbot`` (selects the URDF, EKF, and Nav2 config)

See the `movensys-navigation <https://github.com/movensys/movensys-navigation>`_
repository for the full host setup and container build, and
:doc:`../examples/movensys_navigation_setup` for the example stack.

Running Nav2
------------

Bring up the WMX base (one of the execution modes above), then start Nav2. For a
real base:

.. code-block:: bash

   # 1. WMX base, from the WMX R2 container
   wros ros2 launch wmx_r2_package wmx_r2_differential.launch.py \
       use_sim_time:=false \
       'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/diffbot_differential_config.yaml' \
       'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/diffbot_wmx_parameters.xml'

   # 2. Nav2, from the navigation container:
   #    map_server + AMCL + planner/controller/BT servers + EKF + RViz
   nros ros2 launch movensys_navigation_nav2_config navigation.launch.py

For simulation or hardware-in-the-loop, start the simulator bridge first and
pass ``use_sim_time:=true`` to each command:

.. code-block:: bash

   nros ros2 launch movensys_navigation_nav2_config sim_bridge.launch.py use_sim_time:=true
   wros ros2 launch wmx_r2_package wmx_r2_differential.launch.py use_sim_time:=true ...
   nros ros2 launch movensys_navigation_nav2_config navigation.launch.py use_sim_time:=true

Add ``rsp:=false`` to the Nav2 launch when the robot description is already
published by Gazebo or by ``ros2_control``, and ``use_cuvslam:=true`` to use
cuVSLAM. To drive manually rather than plan, use ``base.launch.py`` (EKF and
robot_state_publisher only) with ``teleop_twist_keyboard`` remapped onto
``/cmd_vel_safe``.

To build a map instead of navigating a known one, launch ``mapping.launch.py``
(SLAM Toolbox) in place of ``navigation.launch.py`` and drive the base manually.
The end-to-end walkthroughs — manual driving, SLAM mapping, and autonomous
navigation — are in :doc:`../examples/movensys_navigation`.

.. note::

   Pass ``rsp:=false`` when a backend already publishes ``/robot_description``
   (the Gazebo sim, or the ``ros2_control`` launch), so it is not published
   twice.

Key Interfaces
--------------

Provided by the WMX ``differential_drive_controller`` (``diffbot`` defaults:
``wheel_radius`` 0.095 m, ``wheel_to_wheel`` 0.55 m, control ``rate`` 100 Hz).

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Topic
     - Type
     - Purpose
   * - ``/cmd_vel_safe``
     - ``geometry_msgs/TwistStamped``
     - Base velocity input (from Nav2's ``velocity_smoother`` or teleop)
   * - ``/joint_states``
     - ``sensor_msgs/JointState``
     - Left/right wheel positions and velocities
   * - ``/odom_enc``
     - ``nav_msgs/Odometry``
     - Encoder dead-reckoned odometry; feeds the localization EKF
   * - ``/odom``
     - ``nav_msgs/Odometry``
     - EKF-fused odometry that Nav2 and AMCL consume

A stale-command timeout (``cmd_vel_timeout``, default 0.25 s) zeroes the
wheels if no velocity command arrives, so a stalled planner stops the base.

.. warning::

   This is a functional software timer, not a safety function. It runs in a
   non-real-time ROS 2 node and has no redundancy, no monitoring, and no
   guaranteed stopping time. A physical base needs a separate emergency stop
   that removes drive power — see :doc:`../try_your_robot/safety`.

See Also
--------

- :doc:`moveit2_integration` -- the manipulator (arm) planning counterpart
- :doc:`../examples/movensys_navigation` -- manual driving, SLAM, and
  autonomous navigation walkthroughs
- The `movensys-navigation <https://github.com/movensys/movensys-navigation>`_
  repository for the full base configuration and Nav2 tuning
