ROS2 Services
==============

The WMX ROS2 application provides services for engine management, axis
control, I/O, EtherCAT diagnostics, and gripper operation. Services use
custom types from ``wmx_ros2_message`` plus standard types from ``std_srvs``.

.. list-table:: Service Summary
   :header-rows: 1
   :widths: 33 27 25 15

   * - Service Name
     - Type
     - Node
     - Category
   * - ``/wmx/engine/set_device``
     - ``wmx_ros2_message/srv/SetEngine``
     - ``wmx_engine_node``
     - Engine
   * - ``/wmx/engine/set_comm``
     - ``std_srvs/srv/SetBool``
     - ``wmx_engine_node``
     - Engine
   * - ``/wmx/engine/get_status``
     - ``std_srvs/srv/Trigger``
     - ``wmx_engine_node``
     - Engine
   * - ``/wmx/engine/scan_network``
     - ``std_srvs/srv/Trigger``
     - ``wmx_engine_node``
     - Engine
   * - ``/wmx/axis/set_on``
     - ``wmx_ros2_message/srv/SetAxis``
     - ``wmx_core_motion_node``
     - Axis Control
   * - ``/wmx/axis/clear_alarm``
     - ``wmx_ros2_message/srv/SetAxis``
     - ``wmx_core_motion_node``
     - Axis Control
   * - ``/wmx/axis/set_mode``
     - ``wmx_ros2_message/srv/SetAxis``
     - ``wmx_core_motion_node``
     - Axis Control
   * - ``/wmx/axis/set_polarity``
     - ``wmx_ros2_message/srv/SetAxis``
     - ``wmx_core_motion_node``
     - Axis Control
   * - ``/wmx/axis/set_gear_ratio``
     - ``wmx_ros2_message/srv/SetAxisGearRatio``
     - ``wmx_core_motion_node``
     - Axis Control
   * - ``/wmx/axis/homing``
     - ``wmx_ros2_message/srv/SetAxis``
     - ``wmx_core_motion_node``
     - Axis Control
   * - ``/wmx/io/get_input_bit``
     - ``wmx_ros2_message/srv/GetIoBit``
     - ``wmx_io_node``
     - I/O
   * - ``/wmx/io/get_output_bit``
     - ``wmx_ros2_message/srv/GetIoBit``
     - ``wmx_io_node``
     - I/O
   * - ``/wmx/io/get_input_bytes``
     - ``wmx_ros2_message/srv/GetIoBytes``
     - ``wmx_io_node``
     - I/O
   * - ``/wmx/io/get_output_bytes``
     - ``wmx_ros2_message/srv/GetIoBytes``
     - ``wmx_io_node``
     - I/O
   * - ``/wmx/io/set_output_bit``
     - ``wmx_ros2_message/srv/SetIoBit``
     - ``wmx_io_node``
     - I/O
   * - ``/wmx/io/set_output_bytes``
     - ``wmx_ros2_message/srv/SetIoBytes``
     - ``wmx_io_node``
     - I/O
   * - ``/wmx/ecat/get_network_state``
     - ``wmx_ros2_message/srv/EcatGetNetworkState``
     - ``wmx_ethercat_node``
     - EtherCAT
   * - ``/wmx/ecat/register_read``
     - ``wmx_ros2_message/srv/EcatRegisterRead``
     - ``wmx_ethercat_node``
     - EtherCAT
   * - ``/wmx/ecat/reset_statistics``
     - ``wmx_ros2_message/srv/EcatResetStatistics``
     - ``wmx_ethercat_node``
     - EtherCAT
   * - ``/wmx/ecat/start_hotconnect``
     - ``wmx_ros2_message/srv/EcatStartHotconnect``
     - ``wmx_ethercat_node``
     - EtherCAT
   * - ``/wmx/set_gripper``
     - ``std_srvs/srv/SetBool``
     - ``follow_joint_trajectory_server``
     - Gripper

.. contents:: Service Categories
   :local:
   :depth: 1

Custom Service Types
--------------------

Before reviewing the services, here are the custom service type definitions
from ``wmx_ros2_message``.

**wmx_ros2_message/srv/SetEngine**

.. code-block:: text

   # Request
   bool data           # true = create device, false = close device
   string path         # Device path (e.g., "/opt/lmx/")
   string name         # Device name (e.g., "wmx_ros2_general_test")
   ---
   # Response
   bool success         # true if operation succeeded
   string message       # Human-readable result description

**wmx_ros2_message/srv/SetAxis**

.. code-block:: text

   # Request
   int32[] index        # Axis indices (e.g., [0, 1, 2, 3, 4, 5])
   int32[] data         # Per-axis values (meaning depends on service)
   ---
   # Response
   bool success         # true only if ALL axes succeeded
   string message       # Concatenated per-axis result messages

**wmx_ros2_message/srv/SetAxisGearRatio**

.. code-block:: text

   # Request
   int32[] index            # Axis indices
   float64[] numerator      # Gear ratio numerators (encoder counts)
   float64[] denumerator    # Gear ratio denominators (physical units)
   ---
   # Response
   bool success             # true only if ALL axes succeeded
   string message           # Concatenated per-axis result messages

Engine Management Services
--------------------------

These services manage the WMX engine lifecycle. They are hosted by
``wmx_engine_node`` (source: ``wmx_engine_node.cpp``).

/wmx/engine/set_device
^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75

   * - **Service Type**
     - ``wmx_ros2_message/srv/SetEngine``
   * - **Node**
     - ``wmx_engine_node``
   * - **Purpose**
     - Create or close the WMX device handle

.. list-table:: Request Fields
   :header-rows: 1
   :widths: 20 20 60

   * - Field
     - Type
     - Description
   * - ``data``
     - ``bool``
     - ``true`` to create device, ``false`` to close device
   * - ``path``
     - ``string``
     - LMX(WMX Runtime) installation path (typically ``/opt/lmx/``)
   * - ``name``
     - ``string``
     - Device name assigned via ``SetDeviceName()``

**Behavior when** ``data=true``:

1. Calls ``WMX3Api::CreateDevice(path, DeviceTypeNormal, timeout=10000)``
2. Calls ``WMX3Api::SetDeviceName(name)``
3. On success: ``message="Created a device with name: <name>"``
4. On error: ``success=false``, ``message="Failed to create device. Error=<code> (<description>)"``

**Behavior when** ``data=false``:

1. Calls ``WMX3Api::CloseDevice()``
2. On success: ``message="Device stopped"``
3. On error: ``success=false``, ``message="Failed to close device. Error=<code> (<description>)"``

**Example -- Create device:**

.. code-block:: bash

   ros2 service call /wmx/engine/set_device wmx_ros2_message/srv/SetEngine \
     "{data: true, path: '/opt/lmx/', name: 'my_device'}"

**Example -- Close device:**

.. code-block:: bash

   ros2 service call /wmx/engine/set_device wmx_ros2_message/srv/SetEngine \
     "{data: false, path: '', name: ''}"

/wmx/engine/set_comm
^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75

   * - **Service Type**
     - ``std_srvs/srv/SetBool``
   * - **Node**
     - ``wmx_engine_node``
   * - **Purpose**
     - Start or stop EtherCAT real-time communication

.. list-table:: Request Fields
   :header-rows: 1
   :widths: 20 20 60

   * - Field
     - Type
     - Description
   * - ``data``
     - ``bool``
     - ``true`` to start communication, ``false`` to stop

**Behavior when** ``data=true``:

- Calls ``WMX3Api::StartCommunication(timeout=10000)``
- On success: ``message="Communication is started"``
- On error: ``success=false``, ``message="Failed to start communication. Error=<code> (<description>)"``

**Behavior when** ``data=false``:

- Calls ``WMX3Api::StopCommunication(timeout=10000)``
- On success: ``message="Communication is stopped"``
- On error: ``success=false``, ``message="Failed to stop communication. Error=<code> (<description>)"``

**Example -- Start communication:**

.. code-block:: bash

   ros2 service call /wmx/engine/set_comm std_srvs/srv/SetBool "{data: true}"

**Example -- Stop communication:**

.. code-block:: bash

   ros2 service call /wmx/engine/set_comm std_srvs/srv/SetBool "{data: false}"

/wmx/engine/get_status
^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75

   * - **Service Type**
     - ``std_srvs/srv/Trigger``
   * - **Node**
     - ``wmx_engine_node``
   * - **Purpose**
     - Query the current WMX engine state

This service takes no request parameters. The response ``message`` field
contains one of the following engine states:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - State
     - Meaning
   * - ``Idle``
     - Engine created but not started
   * - ``Running``
     - Engine running, no EtherCAT communication
   * - ``Communicating``
     - EtherCAT real-time cycle is active (normal operating state)
   * - ``Shutdown``
     - Engine is shutting down
   * - ``Unknown``
     - Unrecognized state code
   * - ``Invalid``
     - State code does not match any known value

The ``success`` field is always ``true`` (the status query itself does not
fail).

**Example:**

.. code-block:: bash

   ros2 service call /wmx/engine/get_status std_srvs/srv/Trigger

Expected response when operating normally:

.. code-block:: text

   success: True
   message: "Communicating"

/wmx/engine/scan_network
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75

   * - **Service Type**
     - ``std_srvs/srv/Trigger``
   * - **Node**
     - ``wmx_engine_node``
   * - **Purpose**
     - Trigger an EtherCAT network scan to discover connected slave devices

Calls ``Ecat::ScanNetwork(masterId=0)``. Returns ``success=true`` and a
summary message on success, or ``success=false`` with the WMX error code on
failure.

**Example:**

.. code-block:: bash

   ros2 service call /wmx/engine/scan_network std_srvs/srv/Trigger

Axis Control Services
---------------------

These services control individual servo axes. They are hosted by
``wmx_core_motion_node`` (source: ``wmx_core_motion_node.cpp``). Operations
are applied per-axis based on the ``index`` array in the request. The response
``success`` is ``true`` only if **all** specified axes succeeded.

/wmx/axis/set_on
^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75

   * - **Service Type**
     - ``wmx_ros2_message/srv/SetAxis``
   * - **Node**
     - ``wmx_core_motion_node``
   * - **Purpose**
     - Enable or disable servo drives

.. list-table:: Request Fields
   :header-rows: 1
   :widths: 20 20 60

   * - Field
     - Type
     - Description
   * - ``index``
     - ``int32[]``
     - Axis indices to control (0-5 for a 6-DOF robot)
   * - ``data``
     - ``int32[]``
     - ``1`` to enable (servo on), ``0`` to disable (servo off)

Calls ``CoreMotion::SetServoOn(axis, on_off)`` for each axis. Response
message is concatenated per-axis (e.g., ``"Set axis 0 on. Set axis 1 on."``).

**Example -- Enable all 6 servos:**

.. code-block:: bash

   ros2 service call /wmx/axis/set_on wmx_ros2_message/srv/SetAxis \
     "{index: [0, 1, 2, 3, 4, 5], data: [1, 1, 1, 1, 1, 1]}"

**Example -- Disable all 6 servos:**

.. code-block:: bash

   ros2 service call /wmx/axis/set_on wmx_ros2_message/srv/SetAxis \
     "{index: [0, 1, 2, 3, 4, 5], data: [0, 0, 0, 0, 0, 0]}"

/wmx/axis/clear_alarm
^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75

   * - **Service Type**
     - ``wmx_ros2_message/srv/SetAxis``
   * - **Node**
     - ``wmx_core_motion_node``
   * - **Purpose**
     - Clear amplifier alarm (fault) on specified axes

Calls ``CoreMotion::ClearAmpAlarm(axis)`` for each axis. The ``data`` field
is not used -- only the ``index`` array determines which axes are cleared.

**Example -- Clear alarms on all axes:**

.. code-block:: bash

   ros2 service call /wmx/axis/clear_alarm wmx_ros2_message/srv/SetAxis \
     "{index: [0, 1, 2, 3, 4, 5], data: [0, 0, 0, 0, 0, 0]}"

/wmx/axis/set_mode
^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75

   * - **Service Type**
     - ``wmx_ros2_message/srv/SetAxis``
   * - **Node**
     - ``wmx_core_motion_node``
   * - **Purpose**
     - Set the control mode for each axis

Calls ``CoreMotion::SetAxisCommandMode(axis, mode)`` for each axis.

.. list-table:: Mode Values
   :header-rows: 1
   :widths: 20 30 50

   * - Value
     - Mode
     - Description
   * - ``0``
     - Position (``AxisCommandMode::Position``)
     - Axis accepts absolute/relative position commands
   * - ``1``
     - Velocity (``AxisCommandMode::Velocity``)
     - Axis accepts velocity commands

Invalid mode values are rejected per-axis with the message
``"Invalid mode <value> for axis <index>"``.

**Example -- Set all axes to position mode:**

.. code-block:: bash

   ros2 service call /wmx/axis/set_mode wmx_ros2_message/srv/SetAxis \
     "{index: [0, 1, 2, 3, 4, 5], data: [0, 0, 0, 0, 0, 0]}"

**Example -- Set axis 0 to velocity mode:**

.. code-block:: bash

   ros2 service call /wmx/axis/set_mode wmx_ros2_message/srv/SetAxis \
     "{index: [0], data: [1]}"

/wmx/axis/set_polarity
^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75

   * - **Service Type**
     - ``wmx_ros2_message/srv/SetAxis``
   * - **Node**
     - ``wmx_core_motion_node``
   * - **Purpose**
     - Set the rotation direction polarity for each axis

Calls ``CoreMotion::SetAxisPolarity(axis, polarity)`` for each axis.

.. list-table:: Polarity Values
   :header-rows: 1
   :widths: 20 80

   * - Value
     - Meaning
   * - ``1``
     - Normal direction
   * - ``-1``
     - Reversed direction

Only ``1`` and ``-1`` are accepted. Invalid values are rejected per-axis with
the message ``"Invalid polarity value for axis <index>: <value>"``.

**Example -- Set axis 1 reversed, axis 0 normal:**

.. code-block:: bash

   ros2 service call /wmx/axis/set_polarity wmx_ros2_message/srv/SetAxis \
     "{index: [0, 1], data: [1, -1]}"

/wmx/axis/set_gear_ratio
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75

   * - **Service Type**
     - ``wmx_ros2_message/srv/SetAxisGearRatio``
   * - **Node**
     - ``wmx_core_motion_node``
   * - **Purpose**
     - Configure the encoder gear ratio for each axis

Calls ``CoreMotion::SetGearRatio(axis, numerator, denominator)`` for each
axis. The gear ratio maps encoder counts to physical units (radians):
``position_radians = encoder_counts * (denominator / numerator)``.

**Example -- Set gear ratios for 2 axes:**

.. code-block:: bash

   ros2 service call /wmx/axis/set_gear_ratio \
     wmx_ros2_message/srv/SetAxisGearRatio \
     "{index: [0, 1],
      numerator: [8388608.0, 8388608.0],
      denumerator: [6.28319, 6.28319]}"

/wmx/axis/homing
^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75

   * - **Service Type**
     - ``wmx_ros2_message/srv/SetAxis``
   * - **Node**
     - ``wmx_core_motion_node``
   * - **Purpose**
     - Set the home (zero) position for specified axes

For each axis in ``index``, this service:

1. Reads the current home parameters via ``Config::GetHomeParam()``
2. Sets ``homeType`` to ``Config::HomeType::CurrentPos``
3. Writes updated parameters via ``Config::SetHomeParam()``
4. Starts the homing procedure via ``CoreMotion::StartHome()``
5. **Blocks** on ``CoreMotion::Wait()`` until homing completes

The ``data`` field is not used -- only the ``index`` array determines which
axes are homed.

.. note::

   This service blocks until all axes complete homing. For multiple axes, each
   axis is homed sequentially within the callback.

**Example -- Home all axes at current position:**

.. code-block:: bash

   ros2 service call /wmx/axis/homing wmx_ros2_message/srv/SetAxis \
     "{index: [0, 1, 2, 3, 4, 5], data: [0, 0, 0, 0, 0, 0]}"

Gripper Service
---------------

/wmx/set_gripper
^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75

   * - **Service Type**
     - ``std_srvs/srv/SetBool``
   * - **Node**
     - ``follow_joint_trajectory_server``
   * - **Purpose**
     - Open or close the pneumatic gripper via EtherCAT digital I/O
   * - **Configurable**
     - Service name set via ``wmx_gripper_topic`` parameter

The gripper is controlled through the WMX ``Io::SetOutBit(0, 0, value)``
API, which sets digital output bit 0 on I/O module 0 in the EtherCAT chain.

.. list-table:: Request
   :header-rows: 1
   :widths: 20 20 60

   * - Field
     - Type
     - Description
   * - ``data``
     - ``bool``
     - ``true`` to close gripper (bit=1), ``false`` to open gripper (bit=0)

.. list-table:: Response
   :header-rows: 1
   :widths: 20 20 60

   * - Field
     - Type
     - Description
   * - ``success``
     - ``bool``
     - ``true`` if I/O write succeeded, ``false`` on error
   * - ``message``
     - ``string``
     - ``"Gripper closed successfully"`` / ``"Gripper opened successfully"``
       on success; ``"Failed to close gripper"`` / ``"Failed to open gripper"``
       on error

**Example -- Close gripper:**

.. code-block:: bash

   ros2 service call /wmx/set_gripper std_srvs/srv/SetBool "{data: true}"

**Example -- Open gripper:**

.. code-block:: bash

   ros2 service call /wmx/set_gripper std_srvs/srv/SetBool "{data: false}"

The gripper state is also reflected in the ``/joint_states`` topic. The
``manipulator_state`` node reads the I/O output bit via ``Io::GetOutBit()``
and maps it to the ``picker_1_joint`` and ``picker_2_joint`` values using
the ``gripper_open_value`` and ``gripper_close_value`` parameters.

I/O Services
------------

These services provide direct access to EtherCAT digital I/O. They are hosted
by ``wmx_io_node`` (source: ``wmx_io_node.cpp``). The node becomes active
after ``wmx_engine_node`` publishes ``/wmx/engine/ready``.

Custom service types used:

**wmx_ros2_message/srv/GetIoBit**

.. code-block:: text

   int32 byte   # I/O byte address
   int32 bit    # Bit index within the byte (0–7)
   ---
   bool success    # true if read succeeded
   int32 value     # Bit value: 0 or 1
   string message  # Response or error description

**wmx_ros2_message/srv/GetIoBytes**

.. code-block:: text

   int32 byte    # Starting I/O byte address
   int32 length  # Number of bytes to read (must be > 0)
   ---
   bool success   # true if read succeeded
   uint8[] data   # Byte values read from I/O
   string message # Response or error description

**wmx_ros2_message/srv/SetIoBit**

.. code-block:: text

   int32 byte   # Output I/O byte address
   int32 bit    # Bit index within the byte (0–7)
   int32 value  # Bit value to write: 0 or 1
   ---
   bool success    # true if write succeeded
   string message  # Response or error description

**wmx_ros2_message/srv/SetIoBytes**

.. code-block:: text

   int32 byte    # Starting output I/O byte address
   uint8[] data  # Byte values to write
   ---
   bool success    # true if write succeeded
   string message  # Response or error description

/wmx/io/get_input_bit
^^^^^^^^^^^^^^^^^^^^^^^

Read a single bit from an EtherCAT digital input.

**Example -- Read input bit 3 of byte 0:**

.. code-block:: bash

   ros2 service call /wmx/io/get_input_bit wmx_ros2_message/srv/GetIoBit \
     "{byte: 0, bit: 3}"

/wmx/io/get_output_bit
^^^^^^^^^^^^^^^^^^^^^^^^

Read the current value of a digital output bit (reads back the commanded
output state, not a physical input).

**Example:**

.. code-block:: bash

   ros2 service call /wmx/io/get_output_bit wmx_ros2_message/srv/GetIoBit \
     "{byte: 0, bit: 0}"

/wmx/io/get_input_bytes
^^^^^^^^^^^^^^^^^^^^^^^^^

Read a contiguous block of digital input bytes.

**Example -- Read 4 input bytes starting at address 0:**

.. code-block:: bash

   ros2 service call /wmx/io/get_input_bytes wmx_ros2_message/srv/GetIoBytes \
     "{byte: 0, length: 4}"

/wmx/io/get_output_bytes
^^^^^^^^^^^^^^^^^^^^^^^^^^

Read the current values of a contiguous block of digital output bytes.

**Example:**

.. code-block:: bash

   ros2 service call /wmx/io/get_output_bytes wmx_ros2_message/srv/GetIoBytes \
     "{byte: 0, length: 4}"

/wmx/io/set_output_bit
^^^^^^^^^^^^^^^^^^^^^^^^

Set a single digital output bit. The ``/wmx/set_gripper`` service uses the
same underlying ``Io::SetOutBit`` call (byte=0, bit=0). Use this service for
general-purpose digital outputs.

**Example -- Set output bit 1 of byte 0 to high:**

.. code-block:: bash

   ros2 service call /wmx/io/set_output_bit wmx_ros2_message/srv/SetIoBit \
     "{byte: 0, bit: 1, value: 1}"

/wmx/io/set_output_bytes
^^^^^^^^^^^^^^^^^^^^^^^^^^

Write a block of digital output bytes in a single call.

**Example -- Write [0x01, 0x00] to output bytes 0–1:**

.. code-block:: bash

   ros2 service call /wmx/io/set_output_bytes wmx_ros2_message/srv/SetIoBytes \
     "{byte: 0, data: [1, 0]}"

EtherCAT Diagnostic Services
-----------------------------

These services provide low-level EtherCAT diagnostics and are hosted by
``wmx_ethercat_node`` (source: ``wmx_ethercat_node.cpp``). The node becomes
active after ``wmx_engine_node`` publishes ``/wmx/engine/ready``.

Custom service types used:

**wmx_ros2_message/srv/EcatGetNetworkState**

.. code-block:: text

   int32 master_id
   ---
   bool success
   string message
   # Master info
   int32 master_state   # EcStateMachine: 0=None 1=Init 2=Preop 4=Boot 8=Safeop 16=Op
   int32 master_mode    # EcMasterMode: 0=Cyclic 1=PP 2=Monitor
   uint32 comm_period
   uint32 total_axes
   uint32 packet_loss
   uint32 over_cycle
   # Per-slave arrays (parallel, one entry per slave)
   int32 num_of_slaves
   int32[] slave_ids
   int32[] slave_states
   bool[] slave_offline
   bool[] slave_inaccessible
   uint32[] slave_vendor_ids
   uint32[] slave_product_codes
   # (plus additional timing and addressing fields)

**wmx_ros2_message/srv/EcatRegisterRead**

.. code-block:: text

   int32 master_id
   int32 slave_id
   int32 reg_address   # valid range: 0x000–0xFFF
   int32 length        # valid range: 1–4096 bytes
   ---
   bool success
   uint8[] data
   string message

**wmx_ros2_message/srv/EcatResetStatistics** / **EcatStartHotconnect**

Both take only ``int32 master_id`` in the request and return
``bool success`` + ``string message``.

/wmx/ecat/get_network_state
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Query the complete EtherCAT network state including master and all slave
devices. Useful for verifying that all drives are online and in operational
state (``slave_states`` = 16).

**Example:**

.. code-block:: bash

   ros2 service call /wmx/ecat/get_network_state \
     wmx_ros2_message/srv/EcatGetNetworkState "{master_id: 0}"

/wmx/ecat/register_read
^^^^^^^^^^^^^^^^^^^^^^^^^

Read raw EtherCAT register data from a specific slave device. Primarily used
for low-level diagnostics.

**Example -- Read 4 bytes from register 0x0130 of slave 1:**

.. code-block:: bash

   ros2 service call /wmx/ecat/register_read \
     wmx_ros2_message/srv/EcatRegisterRead \
     "{master_id: 0, slave_id: 1, reg_address: 304, length: 4}"

/wmx/ecat/reset_statistics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Reset EtherCAT packet counters (packet loss, timeout, over-cycle counts).
Useful when starting a measurement window.

**Example:**

.. code-block:: bash

   ros2 service call /wmx/ecat/reset_statistics \
     wmx_ros2_message/srv/EcatResetStatistics "{master_id: 0}"

/wmx/ecat/start_hotconnect
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Initiate the EtherCAT hot-connect procedure for dynamic slave addition.

**Example:**

.. code-block:: bash

   ros2 service call /wmx/ecat/start_hotconnect \
     wmx_ros2_message/srv/EcatStartHotconnect "{master_id: 0}"

Service Call Workflow
---------------------

For standalone axis control (without MoveIt2), call services in the following
order.

**Setup phase:**

1. ``/wmx/engine/set_device`` -- Create the WMX device
2. ``/wmx/engine/set_comm`` -- Start EtherCAT communication
3. ``/wmx/axis/set_gear_ratio`` -- Configure encoder mapping
4. ``/wmx/axis/set_polarity`` -- Set rotation directions
5. ``/wmx/axis/clear_alarm`` -- Clear any existing faults
6. ``/wmx/axis/set_mode`` -- Select position or velocity mode
7. ``/wmx/axis/set_on`` -- Enable servo drives
8. ``/wmx/axis/homing`` -- Set home position

**Motion phase:**

Use the motion topics (``/wmx/axis/velocity``, ``/wmx/axis/position``,
``/wmx/axis/position/relative``) documented in :doc:`ros2_topics`.

**Shutdown phase:**

1. ``/wmx/axis/set_on`` (data=[0,...]) -- Disable servos
2. ``/wmx/engine/set_comm`` (data=false) -- Stop communication
3. ``/wmx/engine/set_device`` (data=false) -- Close device

Error Handling
--------------

All services follow a consistent error reporting pattern:

- **Engine services** return ``success=false`` with the WMX error code and
  human-readable description in ``message``
- **Axis services** apply operations per-axis and return ``success=true`` only
  if **all** axes succeeded. The ``message`` field contains concatenated
  results for each axis, including error codes for any that failed
- **Error format**: ``"Failed to [operation] axis [N]. Error=[code] ([description])"``
- **Gripper service** returns ``success=false`` with a description if the I/O
  write fails

See Also
--------

- :doc:`ros2_actions` -- FollowJointTrajectory action for MoveIt2 integration
- :doc:`ros2_topics` -- Motion command topics and state feedback
- :doc:`../packages/wmx_ros2_message` -- Custom message type definitions
