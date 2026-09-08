MoveIt2 Motion Planning
========================

Overview
--------

MoveIt2 is the primary motion-planning integration for WMX R2. The
`movensys-manipulator <https://github.com/movensys/movensys-manipulator>`_
repository provides the ``movensys_manipulator_moveit_config`` package, which
wraps MoveIt2 with a high-level service API and executes the planned motion on
the robot through the WMX R2 stack.

MoveIt2 produces collision-aware, time-parameterized trajectories; WMX runs
them on a deterministic real-time cycle. The same configuration drives three
execution modes: pure **simulation** (Isaac Sim or Gazebo), **hardware-in-the-loop**
(simulator visuals with the real WMX runtime), and **real** robot control over
EtherCAT.

Architecture
------------

.. image:: /_static/images/moveIt2_trajectory_flow.png
   :alt: MoveIt2 integration — end-to-end data flow
   :class: with-border
   :align: center

The ``moveit2_api`` node (in ``movensys_manipulator_moveit_config``) hosts
a MoveIt2 ``MoveGroupInterface`` client and exposes simple pose/joint services
under ``/wmx/moveit2/``. For each request it:

1. Sets a joint or Cartesian target on the move group.
2. Plans with MoveIt2 (OMPL), or computes a Cartesian path for straight-line
   moves.
3. Time-parameterizes the trajectory with Time-Optimal Trajectory Generation
   (TOTG), applying velocity and acceleration scaling.
4. Executes it, which streams the trajectory to the WMX
   ``joint_trajectory_controller`` for deterministic execution on the servos.

It also publishes the live end-effector pose on ``/wmx/moveit2/eef_pose``
(``geometry_msgs/PoseStamped``) and orientation on ``/wmx/moveit2/eef_rpy``
(``geometry_msgs/Vector3Stamped``), and calls ``/wmx/set_gripper`` for gripper
actions.

Setup
-----

The MoveIt2 integration runs inside the ``movensys-manipulator`` Docker
container. After cloning the repository and configuring the host environment,
enter the container with the ``mros`` helper. Key environment variables:

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Variable
     - Purpose
   * - ``ROS_DISTRO``
     - ``humble`` or ``jazzy``
   * - ``MANIPULATOR_MODEL``
     - ``dobot_cr3a`` or ``dobot_cr5a`` (selects the MoveIt config)
   * - ``MOVENSYS_ROS_VERSION``
     - ``isaac-ros_4.1``, ``isaac-ros_3.2``, or ``general``
   * - ``CPU_ARCH``
     - ``amd64`` or ``arm64``

See the `movensys-manipulator README
<https://github.com/movensys/movensys-manipulator>`_ for the full host setup,
CycloneDDS buffer tuning, and container build steps.

Running MoveIt2
---------------

Two containers are involved: WMX R2 runs in its own and is launched with
``wros`` (as root, for real-time scheduling); MoveIt2 runs in the
``movensys-manipulator`` container and is launched with ``mros``. Both need
the same ``ROS_DOMAIN_ID`` and ``RMW_IMPLEMENTATION``.

For a real robot:

.. code-block:: bash

   # 1. WMX R2, from the WMX R2 container (see launch_manipulator.md)
   wros ros2 launch wmx_r2_package wmx_r2_manipulator.launch.py \
       use_sim_time:=false \
       'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/cr3a_manipulator_config.yaml' \
       'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/cr3a_wmx_parameters.xml' \
       use_gripper:=true

   # 2. MoveIt2 (move_group + the moveit2_api services), from the
   #    manipulator container
   mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py

   # 3. Run a trajectory test, or send your own service calls
   mros ros2 launch movensys_manipulator_moveit_config trajectory_test.launch.py

Add ``rsp:=false`` to ``moveit.launch.py`` when the robot description is
already published — by Gazebo, or by the ``ros2_control`` launch.

For simulation or hardware-in-the-loop, start the simulator bridge first and
pass ``use_sim_time:=true``:

.. code-block:: bash

   mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py use_sim_time:=true
   mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py \
        use_sim_time:=true

Service API
-----------

The ``moveit2_api`` node exposes these services. Pose services use
``movensys_manipulator_moveit_config/srv/MovePose`` (``pos`` = XYZ metres,
``ori`` = roll/pitch/yaw radians); joint services use ``MoveJoints``.

.. list-table::
   :header-rows: 1
   :widths: 45 30 25

   * - Service
     - Type
     - Purpose
   * - ``/wmx/moveit2/get_eef_pose``
     - ``GetEefPose``
     - Read the current end-effector pose (``pos`` + ``rpy``)
   * - ``/wmx/moveit2/absolute_base_eef_cartesian``
     - ``MovePose``
     - Cartesian move to an absolute pose (base frame)
   * - ``/wmx/moveit2/relative_base_eef_cartesian``
     - ``MovePose``
     - Cartesian move by a relative offset (base frame)
   * - ``/wmx/moveit2/relative_tool_eef_cartesian``
     - ``MovePose``
     - Cartesian move by a relative offset (tool frame)
   * - ``/wmx/moveit2/absolute_base_eef_joint_movement``
     - ``MovePose``
     - Plan to a pose target in joint space (base frame)
   * - ``/wmx/moveit2/eef_pose`` / ``eef_rpy``
     - topics
     - Continuously published end-effector pose and roll/pitch/yaw
   * - ``/wmx/moveit2/joint_movement``
     - ``MoveJoints``
     - Absolute joint-space move
   * - ``/wmx/moveit2/relative_joint_movement``
     - ``MoveJoints``
     - Relative (incremental) joint-space move

Examples
--------

Read the current end-effector pose:

.. code-block:: bash

   mros ros2 service call /wmx/moveit2/get_eef_pose \
        movensys_manipulator_moveit_config/srv/GetEefPose '"{}"'

Absolute Cartesian move (base frame):

.. code-block:: bash

   mros ros2 service call /wmx/moveit2/absolute_base_eef_cartesian \
        movensys_manipulator_moveit_config/srv/MovePose \
        '"{pos: [-0.158, -0.071, 0.346], ori: [3.14159265, 0.0, -3.14159265]}"'

Absolute joint move:

.. code-block:: bash

   mros ros2 service call /wmx/moveit2/joint_movement \
        movensys_manipulator_moveit_config/srv/MoveJoints \
        '"{joint_names: [joint1, joint2, joint3, joint4, joint5, joint6], joint_values: [0.0, 0.0, -1.57, 0.0, 1.57, 0.0]}"'

Open or close the gripper:

.. code-block:: bash

   mros ros2 service call /wmx/set_gripper std_srvs/srv/SetBool '"{data: true}"'

Trajectory Execution
--------------------

Planned trajectories are streamed to the WMX ``joint_trajectory_controller``,
which executes them with cubic spline interpolation
(``AdvancedMotion::StartCSplinePos()``) on a deterministic real-time cycle.
See :doc:`../api_reference/ros2_actions` for the execution details and limits.

See Also
--------

- :doc:`cumotion_integration` -- GPU-accelerated planning with Isaac cuMotion
- :doc:`nav2_integration` -- the mobile-base (Nav2) counterpart to this page
- :doc:`custom_application` -- drive the ``/wmx/moveit2/*`` services from your
  own code
- The `movensys-manipulator <https://github.com/movensys/movensys-manipulator>`_
  repository for the full trajectory, AprilTag, Nvblox, and YOLO walkthroughs
