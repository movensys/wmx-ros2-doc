Testing WMX R2
===============

Once WMX R2 is installed and built, you can validate it in two ways: in
simulation, with no physical hardware, or against real EtherCAT hardware.
Start with simulation, then move to real hardware.

Everything on this page uses the **general nodes** — the five robot-agnostic
nodes in ``wmx_r2_package``. They are the lowest layer of WMX R2: no URDF, no
planner, no robot model. If you can move an axis and read an I/O bit here,
the engine, the EtherCAT bus, and the ROS2 interface are all working.

**Every command on this page runs inside the** ``wmx_r2_container`` **Docker
container**, through the ``wros`` helper — it runs a command in the container
as root, with ROS 2 and the workspace already sourced, and opens an
interactive shell when called with no arguments. Start the container first;
see :doc:`../getting_started/install_wmx3`.

1. Set the operation mode
^^^^^^^^^^^^^^^^^^^^^^^^^

The WMX R2 nodes talk to the WMX engine, which talks to EtherCAT — there is
no built-in mock hardware mode in ROS. The mode is selected in
``/opt/wmx3/Module.ini`` by enabling either the simulation platform or the
EtherCAT platform.

.. note::

   ``Module.ini`` is part of the WMX Runtime, which lives **on the host** at
   ``/opt/wmx3/`` and is bind-mounted into the container. Edit it on the host
   and restart the nodes; there is no need to rebuild the image.

.. tab-set::

   .. tab-item:: Simulation
      :sync: sim

      Disable the EtherCAT platform and enable the simulation platform:

      .. code-block:: ini

         [Platform 0]
         Location = ./platform/ethercat
         DllName = ec_platform.so
         NumOfMaster = 1
         disable = 1

         [Platform 1]
         Location = ./platform/simu
         DllName = simu_platform.so
         NumOfMaster = 1
         disable = 0

   .. tab-item:: Real Hardware
      :sync: real

      This covers any EtherCAT hardware — a robot, a standalone servo drive,
      an I/O module. 

      **Prerequisites**

      - The WMX R2 workspace is built and sourced
      - The WMX Runtime is installed at ``/opt/wmx3/``
      - An EtherCAT cable runs from the compute platform to the first device
      - The hardware and all servo drives are powered on
      - You have ``sudo`` privileges

      **Wiring**

      .. code-block:: text

         ┌──────────────┐    Ethernet     ┌──────────┐    ┌──────────┐         ┌──────────┐
         │  Compute PC  │────(EtherCAT)──►│ Servo J1 │───►│ Servo J2 │── ... ──│ Servo J6 │
         │  (dedicated  │                 └──────────┘    └──────────┘         └──────────┘
         │   NIC port)  │
         └──────────────┘

      - Use a **dedicated Ethernet port** for EtherCAT
      - Servo drives are daisy-chained; each drive has an IN and an OUT port
      - The I/O module for gripper control sits on the same chain

      Enable the EtherCAT platform and disable the simulation platform:

      .. code-block:: ini

         [Platform 0]
         Location = ./platform/ethercat
         DllName = ec_platform.so
         NumOfMaster = 1
         disable = 0

         [Platform 1]
         Location = ./platform/simu
         DllName = simu_platform.so
         NumOfMaster = 1
         disable = 1

.. warning:: **Real Hardware mode moves a physical machine.**

   Start with the Simulation platform. Before switching to EtherCAT and
   enabling servos on a robot, complete :doc:`../try_your_robot/index` —
   parameter validation, the low-speed single-axis procedure, and the
   separate safety measures described in :doc:`../try_your_robot/safety`.

2. Launch the general nodes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The launch file starts five nodes: ``wmx_engine_node``,
``wmx_lifecycle_manager_node``, ``wmx_core_motion_node``, ``wmx_io_node``,
and ``wmx_ethercat_node``.

Launch them inside the WMX R2 container:

.. code-block:: bash

   wros ros2 launch wmx_r2_package wmx_r2_general_nodes.launch.py \
       use_sim_time:=false \
       'config_file:=$(ros2 pkg prefix --share wmx_r2_package)/config/wmx_r2_general_nodes_config.yaml' \
       'wmx_param_file:=$(ros2 pkg prefix --share wmx_r2_package)/config/wmx_parameters.xml'

What happens at startup
"""""""""""""""""""""""

.. mermaid::
   :caption: From launch to a node that answers

   sequenceDiagram
       autonumber
       participant L as launch
       participant E as wmx_engine_node
       participant M as wmx_lifecycle_manager_node
       participant N as wmx_core_motion_node<br/>wmx_io_node<br/>wmx_ethercat_node
       participant W as WMX3 engine

       L->>E: start (ordinary node)
       L->>M: start (ordinary node)
       L->>N: start (lifecycle, unconfigured)
       E->>W: CreateDevice, retry up to 5x on lock error 297
       E->>W: StartCommunication
       W-->>E: Communicating
       loop every discovery_period
           M->>E: get_engine_status
       end
       E-->>M: Communicating
       M->>N: configure
       M->>N: activate
       Note over N: services and topics appear only now

1. **Device creation** — ``wmx_engine_node`` creates the WMX device handle,
   retrying up to five times if another application holds the lock
   (error 297).

2. **Communication start** — ``StartCommunication`` brings up the real-time
   EtherCAT cycle, which discovers the drives on the bus. The engine node
   does this itself at startup; you do not have to call a service.

3. **Bring-up** — ``wmx_lifecycle_manager_node`` polls the engine status. Once
   it reads ``Communicating``, it drives the three lifecycle nodes through
   ``configure`` and ``activate``, in the order given by ``managed_nodes``.

.. important::

   **A lifecycle node advertises nothing until it is** ``active``. If
   ``ros2 service list`` shows no ``/wmx/axes/*``, the node has not been
   brought up — that is not a crash. Check the states first.

3. Typical startup sequence
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The whole path from freshly launched nodes to a first commanded move and back
to a safe stop. Run it once end to end to confirm the stack works; each step
is explained in sections 4 to 7.

These examples command **axis 0 only**. Extend the ``axis`` array to your axis
count — ``axis: [0,1,2,3,4,5]`` for a six-axis arm — keeping ``axis`` and
``data`` the same length.

.. warning:: **Steps 7 and 8 rotate the axis.**

   In Real Hardware mode, do this at low velocity on an axis that is free to
   move, with a hand on the emergency stop, after completing
   :doc:`../try_your_robot/first_motion`.

.. code-block:: bash

   # 1. Check that every node came up.
   wros ros2 service call /wmx/lifecycle/get_node_states \
     wmx_r2_message/srv/GetNodeStates "{}"

   # 2. Check the engine status. The launch already started the EtherCAT
   #    cycle, so this should report "Communicating".
   wros ros2 service call /wmx/engine/get_engine_status std_srvs/srv/Trigger "{}"

   # 3. Set the gear ratio. It defines the user unit of every command below.
   #    8388608 counts (23-bit encoder) per 360 degrees makes one command
   #    unit equal one degree.
   wros ros2 service call /wmx/axes/set_gear_ratio wmx_r2_message/srv/SetAxesGearRatio \
     "{axis: [0], numerator: [8388608.0], denominator: [360.0]}"

   # 4. Clear any amp alarms.
   wros ros2 service call /wmx/axes/clear_amp_alarm wmx_r2_message/srv/SetAxes \
     "{axis: [0], data: [0]}"

   # 5. Enable the servo.
   wros ros2 service call /wmx/axes/set_servo_on wmx_r2_message/srv/SetAxes \
     "{axis: [0], data: [1]}"

   # 6. Home the axis. With the shipped parameter file the current encoder
   #    position becomes zero.
   wros ros2 service call /wmx/axes/start_home wmx_r2_message/srv/SetAxes \
     "{axis: [0], data: [0]}"

   # 7. First move: +10 degrees relative, at low velocity.
   wros ros2 service call /wmx/axes/start_mov wmx_r2_message/srv/StartAxesPose \
     "{axis: [0], target: [10], velocity: [30], acc: [100], dec: [100]}"

   # 8. Or jog by hand instead of step 7. Ctrl+C releases it.
   #    (see section 7 for the loop)

   # 9. Stop the axis.
   wros ros2 service call /wmx/axes/stop wmx_r2_message/srv/SetAxes \
     "{axis: [0], data: [0]}"

   # 10. Turn the servo off. Always do this before stopping communication.
   wros ros2 service call /wmx/axes/set_servo_on wmx_r2_message/srv/SetAxes \
     "{axis: [0], data: [0]}"

Keep a second terminal on the axis feedback while you work through it. After
step 5 ``servo_on`` should be ``true``, after step 6 ``home_done`` should be
``true``, and ``actual_pos`` should follow step 7:

.. code-block:: bash

   wros ros2 topic echo /wmx/axes/status

Then ``Ctrl+C`` the launch terminal to shut down — see section 10.

4. Verify the nodes are up
^^^^^^^^^^^^^^^^^^^^^^^^^^

Each node owns one slice of the interface:

.. list-table::
   :header-rows: 1
   :widths: 28 12 22 38

   * - Node
     - Lifecycle
     - Namespace
     - Owns
   * - ``wmx_engine_node``
     - no
     - ``/wmx/engine/``
     - Device handle, EtherCAT communication, engine status, WMX parameter
       import and inspection
   * - ``wmx_lifecycle_manager_node``
     - no
     - ``/wmx/lifecycle/``
     - Brings every managed node up and down, following the engine
   * - ``wmx_core_motion_node``
     - yes
     - ``/wmx/axes/``
     - Servo on/off, alarms, command mode, polarity, gear ratio, homing,
       stop, motion, and ``/wmx/axes/status``
   * - ``wmx_io_node``
     - yes
     - ``/wmx/io/``
     - Digital input and output, by bit and by byte
   * - ``wmx_ethercat_node``
     - yes
     - ``/wmx/ecat/``
     - Master info, ESC register reads, statistics reset, network scan,
       hot-connect

.. code-block:: bash

   wros ros2 node list                    # expect the five wmx_* nodes
   wros ros2 service list | grep /wmx     # available WMX services
   wros ros2 topic list | grep /wmx       # available WMX topics

   # engine state: expect "Communicating"
   wros ros2 service call /wmx/engine/get_engine_status std_srvs/srv/Trigger "{}"

   # every lifecycle node and its state
   wros ros2 service call /wmx/lifecycle/get_node_states \
        wmx_r2_message/srv/GetNodeStates "{}"

   # EtherCAT master and slave status
   wros ros2 service call /wmx/ecat/get_master_info \
        wmx_r2_message/srv/EcatGetMasterInfo "{master_id: 0}"

If a node is stuck in ``unconfigured``, drive it by hand:

.. code-block:: bash

   wros ros2 service call /wmx/lifecycle/set_node_state wmx_r2_message/srv/SetNodeState \
        "{node_name: 'wmx_core_motion_node', transition: 'bringup'}"

   # or everything at once
   wros ros2 service call /wmx/lifecycle/set_node_state wmx_r2_message/srv/SetNodeState \
        "{node_name: '', transition: 'bringup'}"

``wmx_core_motion_node`` publishes axis feedback at ``axes_status_rate``:

.. code-block:: bash

   wros ros2 topic echo /wmx/axes/status --once

``/wmx/axes/status`` (``wmx_r2_message/msg/AxesStatus``) carries one entry per
axis in each of its arrays: ``amp_alarm``, ``servo_on``, ``home_done``,
``home_switch``, ``negative_ls``, ``positive_ls``, ``motion_complete``,
``pos_cmd``, ``velocity_cmd``, ``actual_pos``, ``actual_velocity``, and
``actual_torque``. It is the single best thing to keep echoing in a second
terminal.

The full interface list is in :doc:`../api_reference/ros2_services` and
:doc:`../api_reference/ros2_topics`, and in the `general nodes reference
<https://github.com/movensys/wmx-r2/blob/main/doc/reference_general_nodes.md>`_.

5. Bring the axes online
^^^^^^^^^^^^^^^^^^^^^^^^

.. warning:: **The general nodes enable no servos.**

   These nodes are robot-agnostic by design. They do not enable the servos —
   that is an explicit ``/wmx/axes/set_servo_on`` call — and if you launch
   them with an empty ``wmx_param_file``, no axis parameters are imported at
   all: the gear ratios, polarities, command modes, and limits in the engine
   are whatever a previous session left there.

   The per-robot launches (``wmx_r2_manipulator.launch.py``,
   ``wmx_r2_differential.launch.py``) pass their own
   ``example/<robot>_wmx_parameters.xml``, and their
   ``joint_state_broadcaster`` enables the servos when it activates. If you
   command motion from the general nodes alone, run the sequence below first.

   See :doc:`../try_your_robot/robot_parameters`.

The sequence is the same in Simulation and Real Hardware mode. The examples
below use six axes; use however many your machine has. The ``axis`` and
``data`` arrays must always be the same length.

**5-1. Read the active axis parameters**

The engine holds whatever axis configuration was last written to it — by a
per-robot launch, by WOS, or by a previous session. Read it back before you
trust it:

.. code-block:: bash

   wros ros2 service call /wmx/engine/get_axis_param wmx_r2_message/srv/GetAxisParam \
        "{axis: [0,1,2,3,4,5]}"

The reply returns one human-readable dump per axis in ``axis_param``, and the
engine must already be communicating. In the dump, ``CommandMode`` is
``0``\ =Position, ``1``\ =Velocity, ``2``\ =Torque; ``HomeType`` is
``0``\ =CurrentPos, ``1``\ =ZPulse, ``2``\ =HS, ``4``\ =HSZPulse; and
``HomeDirection`` is ``0``\ =Positive, ``1``\ =Negative.

To load a parameter file into the running engine without restarting:

.. code-block:: bash

   wros ros2 service call /wmx/engine/import_and_set_all \
        wmx_r2_message/srv/ImportAndSetAll \
        "{path: '/opt/wmx3/wmx_parameters.xml'}"

The path must be absolute.

**5-2. Set the gear ratio**

The gear ratio converts encoder counts into the user units every later command
uses, so get it right before commanding anything. If a per-robot launch has
already applied your robot's parameter file, the ratio is already correct —
confirm it with step 5-1 rather than overwriting it.

For a Panasonic MADLN05BE driver with a 23-bit encoder (8388608 counts per
motor revolution), dividing by 360 makes one command unit equal one degree of
motor shaft rotation:

.. code-block:: bash

   wros ros2 service call /wmx/axes/set_gear_ratio wmx_r2_message/srv/SetAxesGearRatio \
        "{axis: [0], numerator: [8388608.0], denominator: [360.0]}"

.. note::

   Every ``target``, ``velocity``, ``acc``, and ``dec`` value below is in
   these user units — degrees with the ratio above, raw encoder counts with a
   1:1 ratio. Check the ratio before you trust a number, and remember that a
   gearbox between the motor and the joint shifts it again.

**5-3. Clear alarms, enable servos, home**

.. code-block:: bash

   # Clear any amp alarms (data is ignored)
   wros ros2 service call /wmx/axes/clear_amp_alarm wmx_r2_message/srv/SetAxes \
        "{axis: [0,1,2,3,4,5], data: [0,0,0,0,0,0]}"

   # Enable the servos (1 = on, 0 = off)
   wros ros2 service call /wmx/axes/set_servo_on wmx_r2_message/srv/SetAxes \
        "{axis: [0,1,2,3,4,5], data: [1,1,1,1,1,1]}"

   # Home all axes (data is ignored)
   wros ros2 service call /wmx/axes/start_home wmx_r2_message/srv/SetAxes \
        "{axis: [0,1,2,3,4,5], data: [0,0,0,0,0,0]}"

``start_home`` uses the ``HomeType`` configured in the WMX parameter file for
that axis. The shipped files use ``CurrentPos``, which makes the current
encoder position zero. The service does not write the home configuration, so
a switch-based or Z-pulse setup is left alone.

Confirm on ``/wmx/axes/status`` that ``amp_alarm`` is all ``false``,
``servo_on`` all ``true``, and ``home_done`` all ``true`` before commanding
motion.

Two more axis settings are available when a machine needs them:

.. code-block:: bash

   # Command mode: 0 = Position, 1 = Velocity, 2 = Torque
   wros ros2 service call /wmx/axes/set_axis_command_mode wmx_r2_message/srv/SetAxes \
        "{axis: [0,1], data: [0,0]}"

   # Polarity: 1 = normal, -1 = reversed
   wros ros2 service call /wmx/axes/set_axis_polarity wmx_r2_message/srv/SetAxes \
        "{axis: [0,1], data: [1,1]}"

6. Command motion
^^^^^^^^^^^^^^^^^

.. warning:: **These commands rotate the axes.**

   On real hardware, start with one axis, a small relative move, and a low
   velocity, with a hand on the emergency stop. Follow the low-speed
   single-axis procedure in :doc:`../try_your_robot/first_motion` before doing
   this on a robot for the first time.

Motion is a **service call**, not a topic publish. All of them take parallel
arrays, so one call can command several axes at once.

**Absolute position** — move to ``target`` in user units:

.. code-block:: bash

   wros ros2 service call /wmx/axes/start_pos wmx_r2_message/srv/StartAxesPose \
        "{axis: [0,1], target: [45, -90], velocity: [10, 20], \
          acc: [10, 20], dec: [10, 20]}"

**Relative position** — move by ``target`` from wherever the axis is now.
This is the safer of the two for a first move: a small number stays a small
move regardless of where the axis happens to be.

.. code-block:: bash

   wros ros2 service call /wmx/axes/start_mov wmx_r2_message/srv/StartAxesPose \
        "{axis: [0,1], target: [10, -10], velocity: [10, 20], \
          acc: [10, 10], dec: [10, 20]}"

**Continuous velocity** — the axis keeps turning until you stop it. The sign
of ``velocity`` selects the direction.

.. code-block:: bash

   wros ros2 service call /wmx/axes/start_vel wmx_r2_message/srv/StartAxesVelocity \
        "{axis: [0,1], velocity: [10, -10], acc: [10, 20], dec: [10, 20]}"

**Stop** — decelerate to a standstill. ``data`` is ignored:

.. code-block:: bash

   wros ros2 service call /wmx/axes/stop wmx_r2_message/srv/SetAxes \
        "{axis: [0,1], data: [0,0]}"

Watch ``motion_complete`` and ``actual_pos`` to confirm each move finished
where you expected:

.. code-block:: bash

   wros ros2 topic echo /wmx/axes/status --field actual_pos

.. note:: **If a motion service answers** ``success: false``

   While any node listed in ``motion_controllers`` is ``active`` — the
   trajectory, position, and differential controllers — it owns the axes, and
   ``start_pos``, ``start_mov``, ``start_vel``, ``start_jog``, and
   ``start_home`` all refuse. This is deliberate: a manual jog must not fight
   a running trajectory.

   ``stop`` is never blocked. To take manual control, deactivate the
   controller:

   .. code-block:: bash

      wros ros2 service call /wmx/lifecycle/set_node_state \
           wmx_r2_message/srv/SetNodeState \
           "{node_name: 'joint_trajectory_controller', transition: 'deactivate'}"

7. Jog an axis (hold to move)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``/wmx/axes/start_jog`` is a dead-man command: keep calling it to keep moving,
stop calling it to release. ``wmx_core_motion_node`` stops the axis once
refreshes stop arriving (``jog_timeout_ms``, default 200 ms). The sign of
``velocity`` selects the direction.

Jog runs ``Motion::StartJog``, which requires the axis to be in **Position
mode**. After the sequence in section 5:

.. code-block:: bash

   wros ros2 service call /wmx/axes/set_axis_command_mode wmx_r2_message/srv/SetAxes \
        "{axis: [0], data: [0]}"

Then loop the call. ``Ctrl+C`` acts as the release:

.. code-block:: bash

   # positive direction
   while true; do
     wros ros2 service call /wmx/axes/start_jog wmx_r2_message/srv/StartAxesVelocity \
       "{axis: [0], velocity: [10], acc: [100], dec: [100]}"
     sleep 0.05
   done

   # negative direction: negate velocity
   while true; do
     wros ros2 service call /wmx/axes/start_jog wmx_r2_message/srv/StartAxesVelocity \
       "{axis: [0], velocity: [-10], acc: [100], dec: [100]}"
     sleep 0.05
   done

Stop explicitly at any time:

.. code-block:: bash

   wros ros2 service call /wmx/axes/stop wmx_r2_message/srv/SetAxes \
        "{axis: [0], data: [0]}"

**Tuning.** These are ``wmx_core_motion_node`` parameters, read once at
startup — set them in the config YAML, not with ``ros2 param set``:

.. list-table::
   :header-rows: 1
   :widths: 26 14 60

   * - Parameter
     - Default
     - Meaning
   * - ``jog_timeout_ms``
     - ``200.0``
     - Axis stops this long after refreshes stop arriving
   * - ``jog_run_time_ms``
     - ``2000.0``
     - Maximum duration of one jog, enforced engine-side
   * - ``jog_jerk_ratio``
     - ``0.75``
     - Jerk ratio of the jog profile

.. note::

   - ``jog_run_time_ms`` is enforced by the engine, so the axis still stops if
     the calling process dies. Once it elapses the axis stays stopped until
     you release and start again.
   - Repeating the same call only refreshes the dead-man; it does not
     re-issue ``StartJog`` — jog-over-jog override is undefined in WMX3.
   - ``acc`` and ``dec`` are accelerations on the wire but are converted to
     ramp times internally, because the ``TimeAccJerkRatio`` profile used here
     — the same one WOS uses — is time-based.

.. tip::

   For jogging a *robot* rather than a bare axis, use the keyboard teleop in
   ``movensys-manipulator``, which drives the end effector through MoveIt2:

   .. code-block:: bash

      mros ros2 run movensys_manipulator_moveit_config keyboard_teleop

   See :doc:`trajectory_planning`.

8. Read and write digital I/O
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``wmx_io_node`` exposes the EtherCAT I/O image. ``addr`` is the I/O byte
address and ``bit`` is the index within that byte (0–7). Byte values are
decimal on the wire (``15`` = ``0x0F``).

.. code-block:: bash

   # Read a single input bit / output bit
   wros ros2 service call /wmx/io/get_in_bit \
        wmx_r2_message/srv/GetIoBit "{addr: 0, bit: 0}"
   wros ros2 service call /wmx/io/get_out_bit \
        wmx_r2_message/srv/GetIoBit "{addr: 0, bit: 0}"

   # Read scattered bits in one call
   wros ros2 service call /wmx/io/get_in_bits wmx_r2_message/srv/GetIoBits \
        "{addr: [0, 2], bit: [1, 5]}"

   # Read a single byte, or a run of bytes
   wros ros2 service call /wmx/io/get_in_byte \
        wmx_r2_message/srv/GetIoByte "{addr: 0}"
   wros ros2 service call /wmx/io/get_in_bytes \
        wmx_r2_message/srv/GetIoBytes "{addr: 0, size: 4}"

   # Set and clear an output bit (e.g. a gripper solenoid)
   wros ros2 service call /wmx/io/set_out_bit \
        wmx_r2_message/srv/SetIoBit "{addr: 0, bit: 0, data: 1}"
   wros ros2 service call /wmx/io/set_out_bit \
        wmx_r2_message/srv/SetIoBit "{addr: 0, bit: 0, data: 0}"

   # Write output byte 2 to 0x0F, then bytes 2 and 3 to 0x0F and 0x0E
   wros ros2 service call /wmx/io/set_out_byte \
        wmx_r2_message/srv/SetIoByte "{addr: 2, data: 15}"
   wros ros2 service call /wmx/io/set_out_bytes \
        wmx_r2_message/srv/SetIoBytes "{addr: 2, data: [15, 14]}"

A quick way to find which bit a device is wired to: read the input bytes,
toggle the device by hand, read them again.

.. warning::

   In Real Hardware mode ``set_out_bit`` drives real outputs — grippers,
   valves, brakes. Confirm what each output is wired to before writing it.

9. EtherCAT diagnostics
^^^^^^^^^^^^^^^^^^^^^^^

``wmx_ethercat_node`` is where you look when the bus itself is the suspect —
a slave stuck below ``Op``, packet loss, or a drive that does not appear.

.. code-block:: bash

   # Master and per-slave state; master 0 unless you run several rings
   wros ros2 service call /wmx/ecat/get_master_info \
        wmx_r2_message/srv/EcatGetMasterInfo "{master_id: 0}"

The reply gives the master state and mode, the communication period, the
packet-loss, timeout, and over-cycle counters, and parallel arrays describing
every slave — state, AL status code, vendor and product IDs, PDO sizes, axis
count. Master states are ``None``\ =0, ``Init``\ =1, ``Preop``\ =2,
``Boot``\ =4, ``Safeop``\ =8, ``Op``\ =16; modes are ``Cyclic``\ =0,
``PP``\ =1, ``Monitor``\ =2. A healthy running bus reports ``Op`` for the
master and every slave.

.. code-block:: bash

   # Read ESC registers directly (reg_addr is decimal, 0x000-0xFFF)
   wros ros2 service call /wmx/ecat/register_read wmx_r2_message/srv/EcatRegisterRead \
        "{master_id: 0, slave_id: 0, reg_addr: 0, len: 1}"      # 0x000 type
   wros ros2 service call /wmx/ecat/register_read wmx_r2_message/srv/EcatRegisterRead \
        "{master_id: 0, slave_id: 0, reg_addr: 16, len: 4}"     # 0x010 vendor ID
   wros ros2 service call /wmx/ecat/register_read wmx_r2_message/srv/EcatRegisterRead \
        "{master_id: 0, slave_id: 1, reg_addr: 256, len: 16}"   # 0x100 DL status

   # Reset ref-clock and transmit statistics, then re-scan the network
   wros ros2 service call /wmx/ecat/reset_statistics \
        wmx_r2_message/srv/EcatResetStatistics "{master_id: 0}"

   # Re-scan the network for slaves
   wros ros2 service call /wmx/ecat/scan_network \
        wmx_r2_message/srv/EcatScanNetwork "{master_id: 0}"

   # Enable dynamic slave discovery (call once after the network reaches Op)
   wros ros2 service call /wmx/ecat/start_hotconnect \
        wmx_r2_message/srv/EcatStartHotconnect "{master_id: 0}"

``reg_addr + len`` must not exceed ``0x1000`` (4096 bytes).

10. Engine and device control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``wmx_engine_node`` creates the device and starts communication at startup,
so these services are only needed to cycle either one without restarting the
nodes — after changing ``Module.ini``, for instance, or to reproduce a
startup fault.

.. code-block:: bash

   # Stop / start the real-time EtherCAT cycle
   wros ros2 service call /wmx/engine/set_communication \
        std_srvs/srv/SetBool "{data: false}"
   wros ros2 service call /wmx/engine/set_communication \
        std_srvs/srv/SetBool "{data: true}"

   # Close / create the WMX3 device
   wros ros2 service call /wmx/engine/set_engine std_srvs/srv/SetBool "{data: false}"
   wros ros2 service call /wmx/engine/set_engine std_srvs/srv/SetBool "{data: true}"

.. warning::

   Servos must be off before you stop communication. Stopping the cycle under
   an enabled servo drops the drive on a communication fault.

.. note::

   Closing the device takes the managed nodes down with it: the lifecycle
   manager sees the engine leave ``Communicating`` and cleans every node back
   to ``unconfigured``, because their device handles are dead. They come back
   up on their own when the engine returns.

11. Shutdown
^^^^^^^^^^^^

Press ``Ctrl+C`` in the launch terminal. The nodes disable the servos, stop
EtherCAT communication, and close the WMX device.

Next steps
^^^^^^^^^^

- :doc:`movensys_manipulator_setup` — bring up a full manipulator stack
- :doc:`movensys_navigation_setup` — bring up the differential-drive base
- :doc:`../api_reference/api_reference` — the complete interface reference
- :doc:`../try_your_robot/index` — before moving a physical robot
