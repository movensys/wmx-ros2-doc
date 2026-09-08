ROS2 Services
==============

Every WMX R2 command that is not a trajectory is a service call. Motion,
servo power, I/O, EtherCAT diagnostics, engine control, and lifecycle
control are all request/response.

The services come from the five nodes started by
``wmx_r2_general_nodes.launch.py`` plus the gripper controller:

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Node
     - Namespace
     - Provides
   * - ``wmx_engine_node``
     - ``/wmx/engine/*``
     - Device creation, EtherCAT communication, engine status, WMX parameter import
   * - ``wmx_lifecycle_manager_node``
     - ``/wmx/lifecycle/*``
     - Drives every other node through its lifecycle transitions
   * - ``wmx_core_motion_node``
     - ``/wmx/axes/*``
     - Servo power, axis configuration, homing, and single-axis motion
   * - ``wmx_io_node``
     - ``/wmx/io/*``
     - Digital input and output, by bit and by byte
   * - ``wmx_ethercat_node``
     - ``/wmx/ecat/*``
     - Master and slave status, register read, network scan, hot-connect
   * - ``gripper_controller``
     - ``/wmx/set_gripper``
     - Gripper open/close over one WMX output bit

.. important::

   ``wmx_core_motion_node``, ``wmx_io_node``, and ``wmx_ethercat_node`` are
   `managed (lifecycle) nodes
   <https://design.ros2.org/articles/node_lifecycle.html>`_. **They advertise
   their services only while they are** ``active``. If ``ros2 service list``
   shows nothing under ``/wmx/axes/``, the node is not active — check
   ``/wmx/lifecycle/get_node_states`` before assuming the node crashed.
   ``wmx_engine_node`` and ``wmx_lifecycle_manager_node`` are ordinary nodes
   and are always up.

.. contents:: On this page
   :local:
   :depth: 2

Service summary
---------------

.. list-table::
   :header-rows: 1
   :widths: 34 36 30

   * - Service
     - Type
     - Node
   * - ``/wmx/engine/set_engine``
     - ``std_srvs/srv/SetBool``
     - ``wmx_engine_node``
   * - ``/wmx/engine/set_communication``
     - ``std_srvs/srv/SetBool``
     - ``wmx_engine_node``
   * - ``/wmx/engine/get_engine_status``
     - ``std_srvs/srv/Trigger``
     - ``wmx_engine_node``
   * - ``/wmx/engine/import_and_set_all``
     - ``wmx_r2_message/srv/ImportAndSetAll``
     - ``wmx_engine_node``
   * - ``/wmx/engine/get_axis_param``
     - ``wmx_r2_message/srv/GetAxisParam``
     - ``wmx_engine_node``
   * - ``/wmx/lifecycle/set_node_state``
     - ``wmx_r2_message/srv/SetNodeState``
     - ``wmx_lifecycle_manager_node``
   * - ``/wmx/lifecycle/get_node_states``
     - ``wmx_r2_message/srv/GetNodeStates``
     - ``wmx_lifecycle_manager_node``
   * - ``/wmx/axes/set_servo_on``
     - ``wmx_r2_message/srv/SetAxes``
     - ``wmx_core_motion_node``
   * - ``/wmx/axes/clear_amp_alarm``
     - ``wmx_r2_message/srv/SetAxes``
     - ``wmx_core_motion_node``
   * - ``/wmx/axes/set_axis_command_mode``
     - ``wmx_r2_message/srv/SetAxes``
     - ``wmx_core_motion_node``
   * - ``/wmx/axes/set_axis_polarity``
     - ``wmx_r2_message/srv/SetAxes``
     - ``wmx_core_motion_node``
   * - ``/wmx/axes/set_gear_ratio``
     - ``wmx_r2_message/srv/SetAxesGearRatio``
     - ``wmx_core_motion_node``
   * - ``/wmx/axes/start_home``
     - ``wmx_r2_message/srv/SetAxes``
     - ``wmx_core_motion_node``
   * - ``/wmx/axes/stop``
     - ``wmx_r2_message/srv/SetAxes``
     - ``wmx_core_motion_node``
   * - ``/wmx/axes/start_pos``
     - ``wmx_r2_message/srv/StartAxesPose``
     - ``wmx_core_motion_node``
   * - ``/wmx/axes/start_mov``
     - ``wmx_r2_message/srv/StartAxesPose``
     - ``wmx_core_motion_node``
   * - ``/wmx/axes/start_vel``
     - ``wmx_r2_message/srv/StartAxesVelocity``
     - ``wmx_core_motion_node``
   * - ``/wmx/axes/start_jog``
     - ``wmx_r2_message/srv/StartAxesVelocity``
     - ``wmx_core_motion_node``
   * - ``/wmx/io/get_in_bit`` / ``get_out_bit``
     - ``wmx_r2_message/srv/GetIoBit``
     - ``wmx_io_node``
   * - ``/wmx/io/get_in_bits`` / ``get_out_bits``
     - ``wmx_r2_message/srv/GetIoBits``
     - ``wmx_io_node``
   * - ``/wmx/io/get_in_byte`` / ``get_out_byte``
     - ``wmx_r2_message/srv/GetIoByte``
     - ``wmx_io_node``
   * - ``/wmx/io/get_in_bytes`` / ``get_out_bytes``
     - ``wmx_r2_message/srv/GetIoBytes``
     - ``wmx_io_node``
   * - ``/wmx/io/set_out_bit``
     - ``wmx_r2_message/srv/SetIoBit``
     - ``wmx_io_node``
   * - ``/wmx/io/set_out_bits``
     - ``wmx_r2_message/srv/SetIoBits``
     - ``wmx_io_node``
   * - ``/wmx/io/set_out_byte``
     - ``wmx_r2_message/srv/SetIoByte``
     - ``wmx_io_node``
   * - ``/wmx/io/set_out_bytes``
     - ``wmx_r2_message/srv/SetIoBytes``
     - ``wmx_io_node``
   * - ``/wmx/ecat/get_master_info``
     - ``wmx_r2_message/srv/EcatGetMasterInfo``
     - ``wmx_ethercat_node``
   * - ``/wmx/ecat/register_read``
     - ``wmx_r2_message/srv/EcatRegisterRead``
     - ``wmx_ethercat_node``
   * - ``/wmx/ecat/reset_statistics``
     - ``wmx_r2_message/srv/EcatResetStatistics``
     - ``wmx_ethercat_node``
   * - ``/wmx/ecat/scan_network``
     - ``wmx_r2_message/srv/EcatScanNetwork``
     - ``wmx_ethercat_node``
   * - ``/wmx/ecat/start_hotconnect``
     - ``wmx_r2_message/srv/EcatStartHotconnect``
     - ``wmx_ethercat_node``
   * - ``/wmx/set_gripper``
     - ``std_srvs/srv/SetBool``
     - ``gripper_controller``

Every response carries ``bool success`` and ``string message``. On the array
services, ``success`` is true only if **every** entry succeeded, and
``message`` concatenates the per-axis or per-entry results.

Engine services
---------------

``wmx_engine_node`` owns the WMX3 engine and nothing else. It does not move
axes.

/wmx/engine/set_engine
^^^^^^^^^^^^^^^^^^^^^^

Creates the WMX3 device and starts communication. ``data: false`` closes the
device; the managed nodes follow it down within one ``discovery_period``.

.. code-block:: bash

   ros2 service call /wmx/engine/set_engine std_srvs/srv/SetBool "{data: true}"

/wmx/engine/set_communication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starts or stops EtherCAT communication on an already open device.

.. code-block:: bash

   ros2 service call /wmx/engine/set_communication std_srvs/srv/SetBool "{data: true}"

/wmx/engine/get_engine_status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns the engine state in ``message``: ``Idle``, ``Running``,
``Communicating``, ``Shutdown``, or ``Unknown``. ``Communicating`` is the
state every controller waits for.

.. code-block:: bash

   ros2 service call /wmx/engine/get_engine_status std_srvs/srv/Trigger "{}"

/wmx/engine/import_and_set_all
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Imports a WMX3 parameter XML into the running engine. The path must be
absolute.

.. code-block:: bash

   ros2 service call /wmx/engine/import_and_set_all wmx_r2_message/srv/ImportAndSetAll \
     "{path: '/home/admin/workspaces/movensys_ws/install/wmx_r2_package/share/wmx_r2_package/config/wmx_parameters.xml'}"

The same file is normally imported at startup through the launch argument
``wmx_param_file``; this service is for reloading it without restarting.

/wmx/engine/get_axis_param
^^^^^^^^^^^^^^^^^^^^^^^^^^

Dumps the active gear ratio, polarity, and command mode of the requested
axes as one formatted string per axis. Use it to confirm what the engine
actually has, not what the XML says.

.. code-block:: bash

   ros2 service call /wmx/engine/get_axis_param wmx_r2_message/srv/GetAxisParam \
     "{axis: [0,1,2,3,4,5]}"

Lifecycle services
------------------

``wmx_lifecycle_manager_node`` watches the engine and drives every managed
node on the graph. While the engine is communicating it brings each node up
to ``active``; when the engine stops, it takes them back to
``unconfigured``, because their device handles are dead. A node that joins
late or respawns is picked up on the next sweep.

This is not limited to WMX nodes: any managed node in the same namespace is
driven the same way.

/wmx/lifecycle/set_node_state
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Drives one node through a transition. An **empty** ``node_name`` applies the
transition to every lifecycle node found. Transitions that take nodes down
are applied in reverse bring-up order.

``transition`` is one of ``configure``, ``activate``, ``deactivate``,
``cleanup``, ``shutdown``, ``bringup`` (configure + activate), or
``bringdown`` (deactivate).

.. code-block:: bash

   # one node
   ros2 service call /wmx/lifecycle/set_node_state wmx_r2_message/srv/SetNodeState \
     "{node_name: 'wmx_io_node', transition: 'deactivate'}"

   # every node
   ros2 service call /wmx/lifecycle/set_node_state wmx_r2_message/srv/SetNodeState \
     "{node_name: '', transition: 'bringdown'}"

/wmx/lifecycle/get_node_states
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Lists every lifecycle node on the graph with its current state, in bring-up
order.

.. code-block:: bash

   ros2 service call /wmx/lifecycle/get_node_states wmx_r2_message/srv/GetNodeStates "{}"

The standard CLI works too and bypasses the manager:

.. code-block:: bash

   ros2 lifecycle get /wmx_io_node
   ros2 lifecycle set /wmx_io_node activate

.. list-table:: ``wmx_lifecycle_manager_node`` parameters
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Meaning
   * - ``managed_nodes``
     - ``[]``
     - Bring-up order; take-down is the reverse
   * - ``discovery_period``
     - ``2.0``
     - Seconds between engine-state sweeps

Axis services
-------------

``wmx_core_motion_node`` serves both the configuration services and the
manual motion services. ``axis`` and ``data`` arrays must be the same length.

.. danger::

   ``start_pos``, ``start_mov``, ``start_vel``, ``start_jog``, and
   ``start_home`` **rotate the axes**. On a physical robot, complete
   :doc:`../commissioning/index` first.

Configuration and power
^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Service
     - ``data`` meaning
   * - ``/wmx/axes/set_servo_on``
     - ``1`` = servo on, ``0`` = servo off
   * - ``/wmx/axes/clear_amp_alarm``
     - ignored
   * - ``/wmx/axes/set_axis_command_mode``
     - ``0`` = Position, ``1`` = Velocity, ``2`` = Torque
   * - ``/wmx/axes/set_axis_polarity``
     - ``1`` = normal, ``-1`` = reversed
   * - ``/wmx/axes/start_home``
     - ignored
   * - ``/wmx/axes/stop``
     - ignored

.. code-block:: bash

   # servo on axes 0 and 1
   ros2 service call /wmx/axes/set_servo_on wmx_r2_message/srv/SetAxes \
     "{axis: [0,1], data: [1,1]}"

   # clear amplifier alarms
   ros2 service call /wmx/axes/clear_amp_alarm wmx_r2_message/srv/SetAxes \
     "{axis: [0,1], data: [0,0]}"

   # reverse the direction of axis 2
   ros2 service call /wmx/axes/set_axis_polarity wmx_r2_message/srv/SetAxes \
     "{axis: [2], data: [-1]}"

``/wmx/axes/set_gear_ratio`` sets the encoder-count-to-user-unit ratio per
axis. This is the parameter that makes one axis user unit equal one radian
at the joint:

.. code-block:: bash

   ros2 service call /wmx/axes/set_gear_ratio wmx_r2_message/srv/SetAxesGearRatio \
     "{axis: [0,1], numerator: [8388608.0, 8388608.0], denominator: [360.0, 360.0]}"

``/wmx/axes/start_home`` homes with the ``HomeType`` configured **in the WMX
parameter file** for that axis. The shipped parameter files use
``CurrentPos``, which makes the current encoder position zero. The service
does not write the home configuration, so a switch-based or Z-pulse setup is
left alone.

``/wmx/axes/stop`` decelerates the axes to a stop. It is the one motion
service that is never blocked, even while a controller owns the axes.

.. warning::

   ``stop`` is a controlled deceleration, not an emergency stop. A real
   e-stop must be a hardware circuit — see :doc:`../commissioning/safety`.

Manual motion
^^^^^^^^^^^^^

.. code-block:: bash

   # absolute move
   ros2 service call /wmx/axes/start_pos wmx_r2_message/srv/StartAxesPose \
     "{axis: [0,1], target: [45, -90], velocity: [10, 20], acc: [10, 20], dec: [10, 20]}"

   # relative move
   ros2 service call /wmx/axes/start_mov wmx_r2_message/srv/StartAxesPose \
     "{axis: [0,1], target: [10, -10], velocity: [10, 20], acc: [10, 10], dec: [10, 20]}"

   # constant velocity until stopped
   ros2 service call /wmx/axes/start_vel wmx_r2_message/srv/StartAxesVelocity \
     "{axis: [0,1], velocity: [10, -10], acc: [10, 20], dec: [10, 20]}"

``/wmx/axes/start_jog`` is a dead-man jog in Position mode: keep calling it
to keep moving, stop calling it to release. The sign of ``velocity`` selects
the direction.

.. code-block:: bash

   while true; do
     ros2 service call /wmx/axes/start_jog wmx_r2_message/srv/StartAxesVelocity \
       "{axis: [0], velocity: [10], acc: [100], dec: [100]}"
     sleep 0.05
   done

.. list-table:: ``wmx_core_motion_node`` parameters
   :header-rows: 1
   :widths: 27 18 55

   * - Parameter
     - Default
     - Meaning
   * - ``axes_status_rate``
     - ``100``
     - ``/wmx/axes/status`` publish rate, Hz
   * - ``jog_timeout_ms``
     - ``200.0``
     - Axis stops this long after jog refreshes stop arriving
   * - ``jog_run_time_ms``
     - ``2000.0``
     - Maximum duration of one jog, enforced engine-side
   * - ``jog_jerk_ratio``
     - ``0.75``
     - Jerk ratio of the jog profile
   * - ``motion_controllers``
     - ``joint_trajectory_controller``,
       ``differential_drive_controller``,
       ``joint_position_controller``
     - While one is ``active`` it owns the axes; see below
   * - ``controller_resync_period``
     - ``0.2``
     - Seconds between re-queries of each controller's state

Controller arbitration
^^^^^^^^^^^^^^^^^^^^^^

A manual jog must not fight a running trajectory. While any node listed in
``motion_controllers`` is ``active``, ``wmx_core_motion_node`` refuses its
own motion services and answers ``success: false``:

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Blocked while a controller is active
     - Always available
   * - ``start_pos``, ``start_mov``, ``start_vel``, ``start_jog``,
       ``start_home``
     - ``stop``, ``set_servo_on``, ``clear_amp_alarm``,
       ``set_axis_command_mode``, ``set_axis_polarity``, ``set_gear_ratio``

The configuration services stay open because ``joint_state_broadcaster``
itself calls ``set_servo_on`` when it activates.

I/O services
------------

``addr`` is the I/O byte address and ``bit`` is the index inside that byte
(0–7). All ``data`` values are decimal.

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Service
     - Reads / writes
   * - ``/wmx/io/get_in_bit``, ``/wmx/io/get_out_bit``
     - One bit
   * - ``/wmx/io/get_in_bits``, ``/wmx/io/get_out_bits``
     - Scattered bits, one ``data`` entry per ``addr``/``bit`` pair
   * - ``/wmx/io/get_in_byte``, ``/wmx/io/get_out_byte``
     - One byte
   * - ``/wmx/io/get_in_bytes``, ``/wmx/io/get_out_bytes``
     - ``size`` consecutive bytes from ``addr``
   * - ``/wmx/io/set_out_bit``
     - One output bit
   * - ``/wmx/io/set_out_bits``
     - Scattered output bits, together in one SDK call
   * - ``/wmx/io/set_out_byte``
     - One output byte
   * - ``/wmx/io/set_out_bytes``
     - Consecutive output bytes from ``addr``

.. code-block:: bash

   ros2 service call /wmx/io/get_in_bit wmx_r2_message/srv/GetIoBit "{addr: 0, bit: 0}"

   ros2 service call /wmx/io/get_in_bits wmx_r2_message/srv/GetIoBits \
     "{addr: [0, 2], bit: [1, 5]}"

   ros2 service call /wmx/io/get_in_bytes wmx_r2_message/srv/GetIoBytes "{addr: 0, size: 4}"

   ros2 service call /wmx/io/set_out_bit wmx_r2_message/srv/SetIoBit \
     "{addr: 0, bit: 0, data: 1}"

   ros2 service call /wmx/io/set_out_bits wmx_r2_message/srv/SetIoBits \
     "{addr: [0, 2], bit: [1, 5], data: [1, 0]}"

   # 15 = 0x0F
   ros2 service call /wmx/io/set_out_byte wmx_r2_message/srv/SetIoByte "{addr: 2, data: 15}"

   ros2 service call /wmx/io/set_out_bytes wmx_r2_message/srv/SetIoBytes \
     "{addr: 2, data: [15, 14]}"

EtherCAT services
-----------------

/wmx/ecat/get_master_info
^^^^^^^^^^^^^^^^^^^^^^^^^

Reads master and per-slave status. This is the first call to make when the
network does not come up.

.. code-block:: bash

   ros2 service call /wmx/ecat/get_master_info wmx_r2_message/srv/EcatGetMasterInfo \
     "{master_id: 0}"

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Field
     - Values
   * - ``state``
     - ``0`` None, ``1`` Init, ``2`` Preop, ``4`` Boot, ``8`` Safeop, ``16`` Op
   * - ``mode``
     - ``0`` Cyclic, ``1`` PP, ``2`` Monitor

The response also carries the communication period, the total axis count,
the transmit-delay and packet-loss counters, and one entry per slave in the
parallel ``slave_*`` arrays (state, AL status code, vendor/product ID,
input/output address and size, axis count). A slave stuck in ``Preop`` with
a non-zero ``slave_al_status_codes`` entry is the usual failure.

/wmx/ecat/register_read
^^^^^^^^^^^^^^^^^^^^^^^

Reads ``len`` bytes from a slave ESC register. ``reg_addr`` is decimal, in
the range ``0x000``–``0xFFF``, with ``reg_addr + len`` ≤ ``0x1000``.

.. code-block:: bash

   ros2 service call /wmx/ecat/register_read wmx_r2_message/srv/EcatRegisterRead \
     "{master_id: 0, slave_id: 0, reg_addr: 16, len: 4}"

/wmx/ecat/reset_statistics
^^^^^^^^^^^^^^^^^^^^^^^^^^

Resets the reference-clock and transmit statistics, then re-scans the
network.

.. code-block:: bash

   ros2 service call /wmx/ecat/reset_statistics wmx_r2_message/srv/EcatResetStatistics \
     "{master_id: 0}"

/wmx/ecat/scan_network
^^^^^^^^^^^^^^^^^^^^^^

Re-scans the network for slaves.

.. code-block:: bash

   ros2 service call /wmx/ecat/scan_network wmx_r2_message/srv/EcatScanNetwork "{master_id: 0}"

/wmx/ecat/start_hotconnect
^^^^^^^^^^^^^^^^^^^^^^^^^^

Enables dynamic slave discovery. Call it once, after the network has reached
``Op``.

.. code-block:: bash

   ros2 service call /wmx/ecat/start_hotconnect wmx_r2_message/srv/EcatStartHotconnect \
     "{master_id: 0}"

Gripper service
---------------

/wmx/set_gripper
^^^^^^^^^^^^^^^^

Served by ``gripper_controller``, which is started only when the manipulator
launch is given ``use_gripper:=true``. The service name comes from the
``wmx_gripper_topic`` parameter (named "topic" for historical reasons — it is
a service).

.. code-block:: bash

   ros2 service call /wmx/set_gripper std_srvs/srv/SetBool "{data: true}"   # close
   ros2 service call /wmx/set_gripper std_srvs/srv/SetBool "{data: false}"  # open

``data: true`` drives the configured output bit to 1, ``false`` to 0. The
bit is set by the ``gripper_address: [byte, bit]`` parameter. The service
returns ``success: false`` when the node is not ``active``.

.. note::

   ``pre_setup_io`` defaults to ``false``. With it false, ``configure`` skips
   the gripper power-up sequence and the service then toggles a bit on an
   unpowered gripper. The power-up addresses are compiled in, so set
   ``pre_setup_io: true`` only if your gripper matches them.

Startup sequence
----------------

The order below is what the manipulator and differential launches perform
automatically. Run it by hand only when using the general nodes on their own.

.. code-block:: bash

   # 1. Verify the engine is communicating
   ros2 service call /wmx/engine/get_engine_status std_srvs/srv/Trigger "{}"

   # 2. Set the gear ratio (encoder counts per user unit)
   ros2 service call /wmx/axes/set_gear_ratio wmx_r2_message/srv/SetAxesGearRatio \
     "{axis: [0, 1], numerator: [8388608.0, 8388608.0], denominator: [360.0, 360.0]}"

   # 3. Clear any amplifier alarms
   ros2 service call /wmx/axes/clear_amp_alarm wmx_r2_message/srv/SetAxes \
     "{axis: [0,1], data: [0,0]}"

   # 4. Enable the servos
   ros2 service call /wmx/axes/set_servo_on wmx_r2_message/srv/SetAxes \
     "{axis: [0,1], data: [1,1]}"

   # 5. Home the axes
   ros2 service call /wmx/axes/start_home wmx_r2_message/srv/SetAxes \
     "{axis: [0,1], data: [0,0]}"

.. mermaid::
   :caption: General-node startup, from engine to a moving axis

   sequenceDiagram
       autonumber
       participant U as You / launch file
       participant E as wmx_engine_node
       participant L as wmx_lifecycle_manager_node
       participant M as wmx_core_motion_node
       participant W as WMX3 engine

       U->>E: set_engine (data: true)
       E->>W: CreateDevice + start communication
       W-->>E: Communicating
       L->>E: get_engine_status (every discovery_period)
       E-->>L: Communicating
       L->>M: configure, then activate
       Note over M: services /wmx/axes/* appear only now
       U->>M: set_gear_ratio
       U->>M: clear_amp_alarm
       U->>M: set_servo_on
       U->>M: start_home
       U->>M: start_pos
       M->>W: CoreMotion StartPos
       W-->>M: motionComplete + inPos

Error handling
--------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Symptom
     - Cause
   * - ``ros2 service list`` shows no ``/wmx/axes/*``
     - The node is not ``active``. Check
       ``/wmx/lifecycle/get_node_states``.
   * - ``success: false``, message mentions a controller
     - A node in ``motion_controllers`` is active and owns the axes. Use
       ``stop``, or deactivate the controller.
   * - ``success: false`` on one axis, true on the rest
     - Array services are all-or-nothing in ``success`` but per-entry in
       ``message``. Read ``message``.
   * - ``ArgumentOutOfRange``
     - An ``axis`` index outside ``[0, maxAxes)``.
   * - Service call hangs
     - The engine is not communicating. Check
       ``/wmx/engine/get_engine_status`` first.

.. note::

   Node parameters are read once at startup. ``ros2 param set`` is accepted
   by rclcpp but changes nothing — edit the config YAML and restart the node.

See also
--------

- :doc:`ros2_topics` -- published and subscribed topics
- :doc:`ros2_actions` -- the ``FollowJointTrajectory`` action
- :doc:`wmx_r2_message` -- message and service definitions
- :doc:`wmx_r2_package` -- nodes, launch files, and configuration
- :doc:`../troubleshooting/troubleshooting` -- diagnosis by symptom
