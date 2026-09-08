wmx_r2_control
==============

Overview
--------

``wmx_r2_control`` is the ``ros2_control`` route into WMX R2. It provides a
``SystemInterface`` plugin — ``wmx_r2_control/WmxSystemHardware`` — that
exposes WMX3 axes to the standard ``controller_manager``, plus the URDF
xacros, controller YAMLs, and launch files that use it.

It is an **alternative** to the direct route, not a replacement. Use it when
you want stock ``ros2_controllers`` (``diff_drive_controller``,
``joint_state_broadcaster``) rather than the WMX-specific controllers in
``wmx_r2_package``.

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * -
     - Direct (``wmx_r2_package``)
     - ``ros2_control`` (``wmx_r2_control``)
   * - Feedback
     - ``joint_state_broadcaster`` node reads WMX3 directly
     - ``WmxSystemHardware`` ``read()`` into standard
       ``joint_state_broadcaster/JointStateBroadcaster``
   * - Arm motion
     - ``joint_trajectory_controller`` → WMX3 C-spline
     - **the same node** — ``ros2_control`` handles feedback only
   * - Wheel motion
     - ``differential_drive_controller`` → ``StartVel``
     - ``diff_drive_controller/DiffDriveController`` →
       ``WmxSystemHardware`` ``write()`` → ``StartVel``
   * - Extra processes
     - none
     - ``ros2_control_node``, ``robot_state_publisher``, spawners

Package structure
-----------------

.. code-block:: text

   wmx_r2_control/
   ├── src/wmx_system_hardware.cpp        # the SystemInterface plugin
   ├── include/wmx_r2_control/wmx_system_hardware.hpp
   ├── wmx_r2_control_plugin.xml          # pluginlib export
   ├── launch/
   │   ├── wmx_r2_control_manipulator.launch.py
   │   └── wmx_r2_control_differential.launch.py
   ├── urdf/
   │   ├── cr3a.wmx.urdf.xacro       cr3a.wmx.ros2_control.xacro
   │   ├── cr5a.wmx.urdf.xacro       cr5a.wmx.ros2_control.xacro
   │   └── diffbot.wmx.urdf.xacro    diffbot.wmx.ros2_control.xacro
   ├── config/
   │   ├── cr3a_controllers.yaml
   │   ├── cr5a_controllers.yaml
   │   └── diffbot_controllers.yaml
   ├── CMakeLists.txt
   └── package.xml

WmxSystemHardware
-----------------

The plugin attaches to the engine that ``wmx_engine_node`` owns. **It does
not start or stop the engine** — the general nodes still do that, which is
why both ``ros2_control`` launch files include
``wmx_r2_general_nodes.launch.py``.

Hardware parameters
^^^^^^^^^^^^^^^^^^^

Set in the ``<hardware>`` block of the ``ros2_control`` xacro:

.. list-table::
   :header-rows: 1
   :widths: 24 76

   * - Parameter
     - Meaning
   * - ``device_name``
     - WMX device name for this hardware instance, e.g. ``wmx_cr3a_control``
   * - ``wmx_param_file``
     - WMX3 parameter XML; passed in from the launch argument of the same
       name

Per-joint parameters
^^^^^^^^^^^^^^^^^^^^

Each ``<joint>`` needs one ``<param name="axis">`` giving its WMX3 axis
index. An axis outside ``[0, maxAxes)`` fails initialization.

Interfaces
^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 26 20 54

   * - Interface
     - Direction
     - Notes
   * - ``position``
     - state
     - WMX ``actualPos``, unconverted
   * - ``velocity``
     - state
     - WMX ``actualVelocity``
   * - ``velocity``
     - command
     - Written with CoreMotion ``StartVel``

A joint declares **either** a single ``velocity`` command interface **or**
no command interface at all, which makes it state-only. Anything else fails
initialization.

.. note::

   There is no ``position`` command interface. The arm's planned motion goes
   through ``wmx_r2_package``'s ``joint_trajectory_controller``, which talks
   to the WMX C-spline directly — ``ros2_control`` is not in that path.
   ``cr3a.wmx.ros2_control.xacro`` and ``cr5a.wmx.ros2_control.xacro``
   therefore declare state interfaces only.

Launch files
------------

wmx_r2_control_manipulator.launch.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starts, in order:

1. ``wmx_r2_general_nodes.launch.py`` — engine, lifecycle manager, axes,
   I/O, EtherCAT
2. ``robot_state_publisher`` from ``urdf_file``
3. ``ros2_control_node`` with ``controllers_file``
4. the ``joint_state_broadcaster`` spawner (standard ``ros2_controllers``)
5. ``joint_trajectory_controller``, ``joint_position_controller``, and —
   with ``use_gripper:=true`` — ``gripper_controller``, all from
   ``wmx_r2_package``
6. a ``topic_tools`` relay for the Isaac Sim joint command mirror

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
     - Manipulator node parameters, e.g.
       ``wmx_r2_package/example/cr3a_manipulator_config.yaml``
   * - ``wmx_param_file``
     - **required**
     - WMX3 parameter XML. Required here, not optional: it is also fed to the
       xacro, so an empty value would blank the description's own default.
   * - ``urdf_file``
     - **required**
     - Robot description xacro, e.g. ``urdf/cr3a.wmx.urdf.xacro``
   * - ``controllers_file``
     - **required**
     - ``controller_manager`` YAML, e.g. ``config/cr3a_controllers.yaml``
   * - ``use_gripper``
     - ``false``
     - Start ``gripper_controller``

.. code-block:: bash

   wros ros2 launch wmx_r2_control wmx_r2_control_manipulator.launch.py \
       use_sim_time:=false \
       'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/cr3a_manipulator_config.yaml' \
       'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/cr3a_wmx_parameters.xml' \
       'urdf_file:=$(ros2 pkg prefix --share wmx_r2_control)/urdf/cr3a.wmx.urdf.xacro' \
       'controllers_file:=$(ros2 pkg prefix --share wmx_r2_control)/config/cr3a_controllers.yaml' \
       use_gripper:=true

wmx_r2_control_differential.launch.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Same shape, minus ``use_gripper``. Here ``ros2_control`` **does** own the
motion: the spawned ``diff_drive_controller/DiffDriveController`` writes
wheel velocities into ``WmxSystemHardware``, which calls ``StartVel``.

.. code-block:: bash

   wros ros2 launch wmx_r2_control wmx_r2_control_differential.launch.py \
       use_sim_time:=false \
       'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/diffbot_differential_config.yaml' \
       'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/example/diffbot_wmx_parameters.xml' \
       'urdf_file:=$(ros2 pkg prefix --share wmx_r2_control)/urdf/diffbot.wmx.urdf.xacro' \
       'controllers_file:=$(ros2 pkg prefix --share wmx_r2_control)/config/diffbot_controllers.yaml'

Controller configuration
------------------------

``cr3a_controllers.yaml`` loads only the state broadcaster, because the arm's
motion controllers are not ``ros2_control`` controllers:

.. code-block:: yaml

   controller_manager:
     ros__parameters:
       update_rate: 100
       joint_state_broadcaster:
         type: joint_state_broadcaster/JointStateBroadcaster

``diffbot_controllers.yaml`` adds the diff-drive controller:

.. code-block:: yaml

   controller_manager:
     ros__parameters:
       update_rate: 100
       joint_state_broadcaster:
         type: joint_state_broadcaster/JointStateBroadcaster
       differential_drive_controller:
         type: diff_drive_controller/DiffDriveController

   differential_drive_controller:
     ros__parameters:
       left_wheel_names: ["drivewheel_left_joint"]
       right_wheel_names: ["drivewheel_right_joint"]
       wheel_separation: 0.55
       wheel_radius: 0.095
       publish_rate: 100.0
       odom_frame_id: odom
       base_frame_id: base_link
       enable_odom_tf: false
       use_stamped_vel: true
       cmd_vel_timeout: 0.25
       # all limiters off - see the note below
       linear.x.has_velocity_limits: false
       linear.x.has_acceleration_limits: false
       linear.x.has_jerk_limits: false
       angular.z.has_velocity_limits: false
       angular.z.has_acceleration_limits: false
       angular.z.has_jerk_limits: false

.. important::

   The limiters are **deliberately disabled**. ``diff_drive_controller``
   enables velocity, acceleration, and jerk limiting by default, and with
   ``max_deceleration`` and ``max_jerk`` unset the braking ramp is poor. With
   the limiters off, the controller is a pure passthrough and the
   ``StartVel`` profile plus the WMX-side axis limits do the shaping — which
   matches how ``wmx_r2_package``'s own differential controller behaves.

   ``enable_odom_tf`` is ``false`` for the same reason ``publish_tf`` is
   false on the direct controller: the localization EKF owns the
   ``odom → base_link`` transform.

   ``use_sim_time`` is set by the launch file and auto-propagated to every
   loaded controller. Do not hard-code it in the YAML.

See also
--------

- :doc:`wmx_r2_package` -- the nodes the direct route uses
- :doc:`ros2_topics` -- what each route publishes
- :doc:`../integration/nav2_integration` -- the differential stack end to end
- :doc:`../integration/moveit2_integration` -- the manipulator stack end to end
