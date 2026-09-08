Testing WMX R2
===============

Once WMX R2 is installed and built, you can validate it in two ways: in
simulation (no physical hardware required) or against real EtherCAT hardware.
Start with simulation to verify basic behavior, then move to real hardware.

1. Setup Operation Mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


The WMX R2 nodes communicate directly with the WMX engine over EtherCAT —
there is no built-in mock hardware mode. The mode is selected in
``/opt/wmx3/Module.ini`` by enabling either the simulation or the EtherCAT
platform. Select your mode below, then continue with the common test steps
that follow.


.. warning:: **Real Hardware mode moves a physical machine.**

   Start with the Simulation platform. Before switching to EtherCAT and
   enabling servos on a robot, complete :doc:`../commissioning/index` —
   parameter validation, the low-speed single-axis procedure, and the separate
   safety measures described in :doc:`../commissioning/safety`.


.. tab-set::

   .. tab-item:: Simulation
      :sync: sim

      Use the simulation platform to test without any physical hardware
      connected.

      **Setup WMX in simulation mode**

      Modify ``/opt/wmx3/Module.ini`` to disable the EtherCAT platform and
      enable the simulation platform:

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

      This covers testing against any EtherCAT hardware (a robot, a standalone
      servo drive, an I/O module, etc.). The examples below use the Dobot CR3A
      manipulator, but the same procedure applies to any EtherCAT device.

      **Prerequisites**

      - The WMX R2 workspace is built and sourced
      - The WMX Runtime is installed at ``/opt/wmx3/``
      - EtherCAT cable is connected between compute platform and first EtherCAT device
      - The hardware and all servo drives are powered on
      - You have ``sudo`` privileges

      **EtherCAT Wiring**

      .. code-block:: text

         ┌──────────────┐    Ethernet     ┌──────────┐    ┌──────────┐         ┌──────────┐
         │  Compute PC  │────(EtherCAT)──►│ Servo J1 │───►│ Servo J2 │── ... ──│ Servo J6 │
         │  (dedicated  │                 └──────────┘    └──────────┘         └──────────┘
         │   NIC port)  │
         └──────────────┘

      - Use a **dedicated Ethernet port** for EtherCAT
      - Servo drives are daisy-chained (each drive has IN and OUT ports)
      - The I/O module for gripper control is part of the same chain

      **Setup WMX in real hardware mode**

      Modify ``/opt/wmx3/Module.ini`` to enable the EtherCAT platform and
      disable the simulation platform:

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




2. Launch the General Nodes (Standalone)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Start the four robot-agnostic nodes (``wmx_engine_node``, ``wmx_core_motion_node``, ``wmx_io_node``, and ``wmx_ethercat_node``).

.. code-block:: bash

   sudo --preserve-env=PATH \
     --preserve-env=AMENT_PREFIX_PATH \
     --preserve-env=COLCON_PREFIX_PATH \
     --preserve-env=PYTHONPATH \
     --preserve-env=LD_LIBRARY_PATH \
     --preserve-env=ROS_DISTRO \
     --preserve-env=ROS_VERSION \
     --preserve-env=ROS_PYTHON_VERSION \
     --preserve-env=ROS_DOMAIN_ID \
     --preserve-env=RMW_IMPLEMENTATION \
     bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && source $HOME/workspaces/movensys_ws/install/setup.bash && \
     ros2 launch wmx_r2_package wmx_r2_general_nodes.launch.py"


.. note::

   1. **Device creation** -- ``wmx_engine_node`` creates the WMX device handle,
   retrying up to five times if another application holds the lock
   (error 297). The remaining nodes then attach to that device.
   
   2. **Communication start** -- ``StartCommunication`` brings up the real-time
   EtherCAT cycle, which discovers the drives on the bus.
   
   3. **Ready** -- ``wmx_engine_node`` and ``wmx_core_motion_node`` publish a
   latched flag on ``/wmx/engine/ready`` and ``/wmx/core_motion/ready``;
   ``wmx_io_node`` and ``wmx_ethercat_node`` wait on ``/wmx/engine/ready``
   before attaching. Each node then begins serving its services and topics.



3. Typical Startup Sequence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


This is the whole path from freshly launched nodes to a first commanded move
and back to a safe stop. Run it once end to end to confirm the stack works;
each step is explained in detail in sections 4 to 7.

The examples command **axis 0 only**. Extend the ``index`` array to your axis
count — ``index: [0,1,2,3,4,5]`` for a six-axis arm — keeping ``index`` and
``data`` the same length.

.. warning:: **Steps 8 and 9 rotate the axis.**

   In Real Hardware mode, do this at low velocity on an axis that is free to
   move, with a hand on the emergency stop, after completing
   :doc:`../commissioning/first_motion`.

.. code-block:: bash

   # 1. Check the engine status. The launch file already started the EtherCAT
   #    cycle, so this should report "Communicating".
   ros2 service call /wmx/engine/get_status std_srvs/srv/Trigger "{}"

   # 2. Start the EtherCAT cycle by hand. 
   #    Needed only if step 1 did not report "Communicating".
   # ros2 service call /wmx/engine/set_comm std_srvs/srv/SetBool "{data: true}"

   # 3. Set the gear ratio. It defines the user unit of every command below.
   #    8388608 pulses (23-bit encoder) per 360 degrees makes one command unit
   #    one degree.
   ros2 service call /wmx/axis/set_gear_ratio wmx_r2_message/srv/SetAxisGearRatio \
     "{index: [0], numerator: [8388608.0], denominator: [360.0]}"

   # 4. Clear any amp alarms.
   ros2 service call /wmx/axis/clear_alarm wmx_r2_message/srv/SetAxis "{index: [0], data: [0]}"

   # 5. Enable the servo.
   ros2 service call /wmx/axis/set_on wmx_r2_message/srv/SetAxis "{index: [0], data: [1]}"

   # 6. Home the axis. The current encoder position becomes zero.
   ros2 service call /wmx/axis/homing wmx_r2_message/srv/SetAxis "{index: [0], data: [0]}"

   # 7. Switch to position mode (0). Required by both position moves and jog.
   ros2 service call /wmx/axis/set_mode wmx_r2_message/srv/SetAxis "{index: [0], data: [0]}"

   # 8. Command the first move, +10 degrees relative at low velocity.
   ros2 topic pub --once /wmx/axis/position/relative wmx_r2_message/msg/AxisPose \
     "{index: [0], target: [10], velocity: [30], acc: [100], dec: [100]}"

   # 9. Jog the axis by hand instead of step 8. It moves while the topic is
   #    published, and Ctrl+C releases it.
   ros2 topic pub -r 20 /wmx/axis/jog wmx_r2_message/msg/AxisVelocity \
     "{index: [0], velocity: [30], acc: [100], dec: [100]}"

   # 10. Stop the axis.
   ros2 service call /wmx/axis/stop wmx_r2_message/srv/SetAxis "{index: [0], data: [0]}"

   # 11. Turn the servo off. Always do this before stopping communication.
   ros2 service call /wmx/axis/set_on wmx_r2_message/srv/SetAxis "{index: [0], data: [0]}"

Keep a second terminal on the axis feedback while you work through it — after
step 5 ``servo_on`` should be ``true``, after step 6 ``home_done`` should be
``true``, and ``actual_pos`` should follow step 8:

.. code-block:: bash

   ros2 topic echo /wmx/axis/state

Then ``Ctrl+C`` the launch terminal to shut down (see section 11).



4. Verify the Nodes Are Up
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


The general nodes expose the WMX engine, axis, I/O, and EtherCAT control
interfaces as ROS2 services and topics. Each node owns one slice of that
interface:

.. list-table::
   :header-rows: 1
   :widths: 28 30 42

   * - Node
     - Namespace
     - Owns
   * - ``wmx_engine_node``
     - ``/wmx/engine/``, ``/wmx/params/``
     - Device handle, EtherCAT communication, network scan, WMX parameter
       inspection
   * - ``wmx_core_motion_node``
     - ``/wmx/axis/``
     - Servo on/off, alarms, command mode, polarity, gear ratio, homing,
       stop, position/velocity/jog commands, ``/wmx/axis/state``
   * - ``wmx_io_node``
     - ``/wmx/io/``
     - Digital input/output bits and bytes
   * - ``wmx_ethercat_node``
     - ``/wmx/ecat/``
     - Network state, ESC register reads, statistics reset, hotconnect

List what is available and confirm the engine is communicating:

.. code-block:: bash

   ros2 node list                                                 # Expect the four wmx_* nodes
   ros2 service list | grep /wmx                                  # Available WMX services
   ros2 topic list | grep /wmx                                    # Available WMX topics
   ros2 service call /wmx/engine/get_status std_srvs/srv/Trigger  # Expect: "Communicating"
   ros2 service call /wmx/ecat/get_network_state \
        wmx_r2_message/srv/EcatGetNetworkState "{master_id: 0}"   # EtherCAT master/slave status

The engine and core-motion nodes publish a latched (``transient_local``)
``ready`` flag once they have attached to the device, so the flag is still
readable long after startup — ask ``echo`` for the matching durability.
``wmx_core_motion_node`` also publishes axis feedback at 100 Hz:

.. code-block:: bash

   ros2 topic echo /wmx/engine/ready --once --qos-durability transient_local
   ros2 topic echo /wmx/core_motion/ready --once --qos-durability transient_local
   ros2 topic echo /wmx/axis/state --once

``/wmx/axis/state`` (``wmx_r2_message/msg/AxisState``) carries one entry per
axis in each of its arrays: ``amp_alarm``, ``servo_on``, ``home_done``,
``home_switch``, ``negative_ls``, ``positive_ls``, ``motion_complete``,
``pos_cmd``, ``velocity_cmd``, ``actual_pos``, ``actual_velocity``, and
``actual_torque``. It is the single best thing to keep echoing in a second
terminal while you work through the steps below.

For the complete list of services, topics, and message types exposed by the
general nodes — engine control, axis motion, I/O, and EtherCAT — see the
`WMX R2 General Nodes reference
<https://github.com/movensys/wmx-r2/blob/main/doc/reference_wmx_r2_general_nodes.md>`_.



5. Bring the Axes Online
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. warning:: **The general nodes load no robot parameters and enable no
   servos.**

   These four nodes are robot-agnostic by design. They do **not** apply a
   ``<robot>_wmx_parameters.xml`` file, so the gear ratios, polarities,
   command modes, and limits in the engine are whatever was left there by a
   previous session — not your robot's values. They also do not enable the
   servos; that is an explicit ``/wmx/axis/set_on`` call.

   Robot parameters are applied by the per-robot launches
   (``wmx_r2_<robot>_manipulator.launch.py`` and
   ``wmx_r2_diffbot_navigation.launch.py``), which pass
   ``wmx_param_file_path`` to their controllers, or by the ``ros2_control``
   hardware plugin. If you command motion from the general nodes alone, you
   must run the startup sequence below first.

   See :doc:`../commissioning/robot_parameters`.

The sequence is the same whether you are in Simulation or Real Hardware mode.
The examples use six axes (``index: [0,1,2,3,4,5]``); use however many axes
your machine actually has — a single axis is ``index: [0]``. The ``index`` and
``data`` arrays must always be the same length.

**5-1. Check the active axis parameters**

The engine holds whatever axis configuration was last written to it — by a
per-robot launch, by WOS, or by a previous session. Read it back before you
trust it:

.. code-block:: bash

   ros2 service call /wmx/params/get wmx_r2_message/srv/GetWmxParams \
        "{index: [0,1,2,3,4,5]}"

The reply returns one human-readable dump per requested axis in
``params_dump``, and the engine must already be communicating. In the dump,
``CommandMode`` is ``0``\ =Position, ``1``\ =Velocity,
``2``\ =Torque; ``HomeType`` is ``0``\ =CurrentPos, ``1``\ =ZPulse,
``2``\ =HS, ``4``\ =HSZPulse; and ``HomeDirection`` is ``0``\ =Positive,
``1``\ =Negative.

**5-2. Set the gear ratio**

The gear ratio converts encoder counts into the user units every later command
is expressed in, so it is the one setting to get right before commanding
anything. If a per-robot launch has already applied your robot's parameter
file, the ratio is already correct — confirm it with step 5-1 rather than
overwriting it. For a Panasonic MADLN05BE driver with a 23-bit encoder
(8388608 counts per motor revolution), dividing by 360 makes one command unit
equal one degree of motor shaft rotation:

.. code-block:: bash

   ros2 service call /wmx/axis/set_gear_ratio wmx_r2_message/srv/SetAxisGearRatio \
        "{index: [0], numerator: [8388608.0], denominator: [360.0]}"

.. note::

   Every ``target``, ``velocity``, ``acc``, and ``dec`` value below is in these
   user units — degrees with the ratio above, raw encoder counts with a 1:1
   ratio. Check the ratio before you trust a number, and remember that gearboxes
   between the motor and the joint shift it again.

**5-3. Clear alarms, enable servos, home**

.. code-block:: bash

   # Clear any amp alarms
   ros2 service call /wmx/axis/clear_alarm wmx_r2_message/srv/SetAxis \
        "{index: [0,1,2,3,4,5], data: [0,0,0,0,0,0]}"

   # Enable the servos (1 = on, 0 = off)
   ros2 service call /wmx/axis/set_on wmx_r2_message/srv/SetAxis \
        "{index: [0,1,2,3,4,5], data: [1,1,1,1,1,1]}"

   # Home all axes — sets the current encoder position as zero
   ros2 service call /wmx/axis/homing wmx_r2_message/srv/SetAxis \
        "{index: [0,1,2,3,4,5], data: [0,0,0,0,0,0]}"

Confirm on ``/wmx/axis/state`` that ``amp_alarm`` is all ``false``,
``servo_on`` all ``true``, and ``home_done`` all ``true`` before commanding
motion.

Two more axis settings are available when a machine needs them:

.. code-block:: bash

   # Command mode: 0 = Position, 1 = Velocity, 2 = Torque
   ros2 service call /wmx/axis/set_mode wmx_r2_message/srv/SetAxis \
        "{index: [0,1], data: [0,0]}"

   # Polarity: 1 = normal, -1 = reversed
   ros2 service call /wmx/axis/set_polarity wmx_r2_message/srv/SetAxis \
        "{index: [0,1], data: [1,1]}"



6. Command Motion
^^^^^^^^^^^^^^^^^^^^^^^^^


.. warning:: **These commands rotate the axes.**

   On real hardware, start with one axis, a small relative move, and a low
   velocity, and keep a hand on the emergency stop. Follow the low-speed
   single-axis procedure in :doc:`../commissioning/first_motion` before doing
   this on a robot for the first time.

All three motion topics take parallel arrays, so one message can command
several axes at once.

**Absolute position** — move to ``target`` in user units:

.. code-block:: bash

   ros2 topic pub --once /wmx/axis/position wmx_r2_message/msg/AxisPose \
        "{index: [0, 1], target: [8388608, 10000], velocity: [1000000, 5000], \
          acc: [100000, 1000], dec: [100000, 1000]}"

**Relative position** — move by ``target`` from wherever the axis is now. This
is the safer of the two for a first move, because a small number stays a small
move regardless of where the axis happens to be:

.. code-block:: bash

   ros2 topic pub --once /wmx/axis/position/relative wmx_r2_message/msg/AxisPose \
        "{index: [0, 1], target: [8388608, 10000], velocity: [1000000, 5000], \
          acc: [100000, 1000], dec: [100000, 1000]}"

**Continuous velocity** — the axis keeps turning until you stop it. The sign of
``velocity`` selects the direction:

.. code-block:: bash

   ros2 topic pub --once /wmx/axis/velocity wmx_r2_message/msg/AxisVelocity \
        "{index: [0, 1], velocity: [1000000, 5000], acc: [100000, 1000], \
          dec: [100000, 1000]}"

**Stop** — decelerate to a standstill. ``data`` is ignored:

.. code-block:: bash

   ros2 service call /wmx/axis/stop wmx_r2_message/srv/SetAxis \
        "{index: [0,1], data: [0,0]}"

Watch ``motion_complete`` and ``actual_pos`` on ``/wmx/axis/state`` to confirm
each move finished where you expected:

.. code-block:: bash

   ros2 topic echo /wmx/axis/state --field actual_pos



7. Jog an Axis (Hold-to-Move)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


``/wmx/axis/jog`` is a dead-man command: the publisher must keep republishing
while the operator holds the control, and ``wmx_core_motion_node`` stops the
axis once refreshes stop arriving (``jog_timeout_ms``, default 200 ms). The
sign of ``velocity`` selects the direction.

Jog runs ``Motion::StartJog``, which requires the axis to be in **Position
mode**. After the startup sequence in step 5:

.. code-block:: bash

   ros2 service call /wmx/axis/set_mode wmx_r2_message/srv/SetAxis \
        "{index: [0], data: [0]}"

.. tab-set::

   .. tab-item:: From the CLI
      :sync: jog-cli

      ``ros2 topic pub -r 20`` supplies the refreshes; ``Ctrl+C`` acts as the
      release.

      .. code-block:: bash

         # Positive direction
         ros2 topic pub -r 20 /wmx/axis/jog wmx_r2_message/msg/AxisVelocity \
              "{index: [0], velocity: [1000], acc: [10000], dec: [10000]}"

         # Negative direction
         ros2 topic pub -r 20 /wmx/axis/jog wmx_r2_message/msg/AxisVelocity \
              "{index: [0], velocity: [-1000], acc: [10000], dec: [10000]}"

   .. tab-item:: With the keyboard
      :sync: jog-keyboard

      ``jog_keyboard_node`` turns key presses into the same refreshes.
      ``a`` = negative, ``d`` = positive, ``q`` = quit. Run it from a terminal,
      not from a launch file — it needs the terminal in raw mode.

      .. code-block:: bash

         ros2 run wmx_r2_package jog_keyboard_node --ros-args \
              -p axis:=0 -p velocity:=1000.0 -p acc:=10000.0 -p dec:=10000.0

      A terminal reports characters, not key releases, so the node treats a key
      as held while auto-repeat characters keep arriving and stops the axis once
      they stop. How quickly a release is noticed therefore equals the keyboard
      repeat delay, which the node measures on the first press and prints:

      .. code-block:: text

         [INFO] Measured a 150 ms key repeat delay, so a released key now stops the axis within 0.21 s.

      That delay belongs to the machine you type on — over SSH that is your own
      PC, not the WMX machine — so shorten it there:

      .. code-block:: bash

         xset r rate 150 30    # on your own PC (660 ms -> 150 ms)
         xset r rate           # restore the default

      macOS and Windows expose the same setting in their keyboard control panel.

Stop explicitly at any time:

.. code-block:: bash

   ros2 service call /wmx/axis/stop wmx_r2_message/srv/SetAxis "{index: [0], data: [0]}"

**Tuning**

.. code-block:: bash

   # wmx_core_motion_node
   ros2 param set /wmx_core_motion_node jog_timeout_ms 200.0    # stop this long after refreshes stop
   ros2 param set /wmx_core_motion_node jog_run_time_ms 2000.0  # max duration of one jog
   ros2 param set /wmx_core_motion_node jog_jerk_ratio 0.75     # profile jerk ratio

``jog_keyboard_node`` takes ``axis``, ``velocity``, ``acc``, ``dec`` (what to
command), ``publish_rate`` (20.0 Hz refresh while a key is held),
``hold_grace_s`` (0.1 s release detection once auto-repeat is flowing),
``initial_grace_s`` (0.8 s before it is, replaced by the measurement), and
``grace_margin_s`` (0.06 s headroom added to the measured repeat delay).

.. note::

   - ``jog_run_time_ms`` is enforced by the engine, so the axis still stops if
     the publishing node dies. Once it elapses the axis stays stopped until the
     operator releases and presses again.
   - Republishing the same velocity only refreshes the dead-man; it does not
     re-issue ``StartJog`` (jog-over-jog override is undefined in WMX3).
   - ``acc``/``dec`` are accelerations on the wire but are converted to ramp
     times internally, because the ``TimeAccJerkRatio`` profile used here — the
     same one WOS uses — is time-based.
   - If the jog stutters right after a key is pressed, lower the terminal key
     repeat delay (``xset r rate 150 30``) or raise ``hold_grace_s``.



8. Read and Write Digital I/O
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


``wmx_io_node`` exposes the EtherCAT I/O image. ``byte`` is the I/O byte
address and ``bit`` is the index within that byte (0–7). Byte values are
decimal on the wire (``15`` = ``0x0F``).

.. code-block:: bash

   # Read a single input bit / output bit
   ros2 service call /wmx/io/get_input_bit  wmx_r2_message/srv/GetIoBit "{byte: 0, bit: 0}"
   ros2 service call /wmx/io/get_output_bit wmx_r2_message/srv/GetIoBit "{byte: 0, bit: 0}"

   # Read a run of bytes
   ros2 service call /wmx/io/get_input_bytes  wmx_r2_message/srv/GetIoBytes "{byte: 0, length: 4}"
   ros2 service call /wmx/io/get_output_bytes wmx_r2_message/srv/GetIoBytes "{byte: 0, length: 4}"

   # Set and clear an output bit (e.g. a gripper solenoid)
   ros2 service call /wmx/io/set_output_bit wmx_r2_message/srv/SetIoBit "{byte: 0, bit: 0, value: 1}"
   ros2 service call /wmx/io/set_output_bit wmx_r2_message/srv/SetIoBit "{byte: 0, bit: 0, value: 0}"

   # Write output byte 2 to 0x0F and byte 3 to 0x0E in one call
   ros2 service call /wmx/io/set_output_bytes wmx_r2_message/srv/SetIoBytes "{byte: 2, data: [15, 14]}"

A quick way to find which bit a device is wired to is to read the input bytes,
toggle the device by hand, and read them again.

.. warning::

   In Real Hardware mode ``set_output_bit`` drives real outputs — grippers,
   valves, brakes. Confirm what each output is wired to before writing it.



9. EtherCAT Diagnostics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


``wmx_ethercat_node`` is where you look when the bus itself is the suspect —
a slave stuck below ``Op``, packet loss, or a drive that does not appear.

.. code-block:: bash

   # Master and per-slave state; master 0 unless you run several rings
   ros2 service call /wmx/ecat/get_network_state \
        wmx_r2_message/srv/EcatGetNetworkState "{master_id: 0}"

The reply gives the master state and mode, the cycle period, packet loss,
timeout and over-cycle counters, and parallel arrays describing every slave
(state, AL status code, vendor and product IDs, PDO sizes, axis count). Master
states are ``None``\ =0, ``Init``\ =1, ``Preop``\ =2, ``Boot``\ =4,
``Safeop``\ =8, ``Op``\ =16; modes are ``CyclicMode``\ =0, ``PPMode``\ =1,
``MonitorMode``\ =2. A healthy running bus reports ``Op`` for the master and
every slave.

.. code-block:: bash

   # Read ESC registers directly (reg_address is decimal, 0x000-0xFFF)
   ros2 service call /wmx/ecat/register_read wmx_r2_message/srv/EcatRegisterRead \
        "{master_id: 0, slave_id: 0, reg_address: 0, length: 1}"    # 0x000 type
   ros2 service call /wmx/ecat/register_read wmx_r2_message/srv/EcatRegisterRead \
        "{master_id: 0, slave_id: 0, reg_address: 16, length: 4}"   # 0x010 vendor ID
   ros2 service call /wmx/ecat/register_read wmx_r2_message/srv/EcatRegisterRead \
        "{master_id: 0, slave_id: 1, reg_address: 256, length: 16}" # 0x100 DL status

   # Reset ref-clock and transmit statistics, then re-scan the network
   ros2 service call /wmx/ecat/reset_statistics \
        wmx_r2_message/srv/EcatResetStatistics "{master_id: 0}"

   # Enable dynamic slave discovery (call once after the network reaches Op)
   ros2 service call /wmx/ecat/start_hotconnect \
        wmx_r2_message/srv/EcatStartHotconnect "{master_id: 0}"

``reg_address + length`` must not exceed ``0x1000`` (4096 bytes). If a drive is
missing entirely, re-scan from the engine node instead:

.. code-block:: bash

   ros2 service call /wmx/engine/scan_network std_srvs/srv/Trigger "{}"



10. Engine and Device Control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


The launch file creates the device and starts communication for you, so these
services are only needed when you want to cycle either one without restarting
the nodes — after changing ``Module.ini``, for instance, or to reproduce a
startup fault.

.. code-block:: bash

   # Stop / start the real-time EtherCAT cycle
   ros2 service call /wmx/engine/set_comm std_srvs/srv/SetBool "{data: false}"
   ros2 service call /wmx/engine/set_comm std_srvs/srv/SetBool "{data: true}"

   # Close / create the WMX3 device handle
   ros2 service call /wmx/engine/set_device wmx_r2_message/srv/SetEngine \
        "{data: false, path: '', name: ''}"
   ros2 service call /wmx/engine/set_device wmx_r2_message/srv/SetEngine \
        "{data: true, path: '/opt/wmx3/', name: 'my_device'}"

.. warning::

   Servos must be off before you stop communication. Stopping the cycle under
   an enabled servo drops the drive on a communication fault.

Standard ROS2 parameter services are available on all four nodes, so
``ros2 param list|get|set <node_name>`` works as usual.



11. Shutdown
^^^^^^^^^^^^^^^^

Press ``Ctrl+C`` in the launch terminal. The nodes will automatically disable
servos, stop EtherCAT communication, and close the WMX device.
