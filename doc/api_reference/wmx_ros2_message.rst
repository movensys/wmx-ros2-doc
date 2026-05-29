wmx_ros2_message
=================

Overview
--------

The ``wmx_ros2_message`` package defines custom ROS2 message and service
interfaces used by all nodes in the WMX ROS2 application. It contains no
executable nodes -- only interface definitions that are compiled into C++
and Python bindings by ``rosidl``.

**Package Metadata:**

.. list-table::
   :widths: 25 75

   * - **Package Name**
     - ``wmx_ros2_message``
   * - **Version**
     - 0.1.0
   * - **License**
     - MIT
   * - **Build Type**
     - ``ament_cmake``

Package Structure
-----------------

.. code-block:: text

   wmx_ros2_message/
   ├── CMakeLists.txt
   ├── package.xml
   ├── msg/
   │   ├── AxisPose.msg
   │   ├── AxisState.msg
   │   └── AxisVelocity.msg
   └── srv/
       ├── SetEngine.srv
       ├── SetAxis.srv
       ├── SetAxisGearRatio.srv
       ├── LoadWmxParams.srv
       ├── GetWmxParams.srv
       ├── GetIoBit.srv
       ├── GetIoBytes.srv
       ├── SetIoBit.srv
       ├── SetIoBytes.srv
       ├── EcatGetNetworkState.srv
       ├── EcatRegisterRead.srv
       ├── EcatResetStatistics.srv
       └── EcatStartHotconnect.srv

Dependencies
------------

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Dependency
     - Type
     - Purpose
   * - ``ament_cmake``
     - buildtool
     - CMake build system
   * - ``rosidl_default_generators``
     - build
     - Message/service code generation
   * - ``std_msgs``
     - depend
     - ``std_msgs/Header`` used by ``AxisState``
   * - ``rosidl_default_runtime``
     - exec
     - Runtime message type support
   * - ``ament_lint_auto`` / ``ament_lint_common`` / ``ament_cmake_gtest``
     - test
     - Linting and tests

The package is a member of the ``rosidl_interface_packages`` group, which
allows other packages to discover its generated interfaces at build time.

Message Definitions
-------------------

AxisPose
^^^^^^^^^

Used for absolute and relative position motion commands. Subscribed by
``wmx_core_motion_node`` on ``/wmx/axis/position`` and
``/wmx/axis/position/relative``.

.. code-block:: text

   int32[]   index       # Axis indices to command
   float64[] target      # Target positions (radians)
   float64[] velocity    # Motion velocity per axis (rad/s)
   float64[] acc         # Acceleration per axis (rad/s²)
   float64[] dec         # Deceleration per axis (rad/s²)

All array fields are parallel -- element ``i`` in each array corresponds to
the same axis.

AxisVelocity
^^^^^^^^^^^^^

Used for continuous velocity motion commands. Subscribed by
``wmx_core_motion_node`` on ``/wmx/axis/velocity``.

.. code-block:: text

   int32[]   index       # Axis indices to command
   float64[] velocity    # Target velocity per axis (rad/s)
   float64[] acc         # Acceleration per axis (rad/s²)
   float64[] dec         # Deceleration per axis (rad/s²)

AxisState
^^^^^^^^^^

Comprehensive per-axis status feedback published at 100 Hz by
``wmx_core_motion_node`` on ``/wmx/axis/state``.

.. code-block:: text

   std_msgs/Header header

   # Status flags (per axis)
   bool[] amp_alarm        # Amplifier alarm active
   bool[] servo_on         # Servo enabled
   bool[] home_done        # Homing completed
   bool[] home_switch      # Home switch triggered
   bool[] negative_ls      # Negative limit switch triggered
   bool[] positive_ls      # Positive limit switch triggered
   bool[] motion_complete  # Motion finished / in position

   # Command and feedback values (per axis)
   float64[] pos_cmd          # Commanded position (radians)
   float64[] velocity_cmd     # Commanded velocity (rad/s)
   float64[] actual_pos       # Actual encoder position (radians)
   float64[] actual_velocity  # Actual velocity (rad/s)
   float64[] actual_torque    # Actual torque

Service Definitions
-------------------

Engine
^^^^^^^

**SetEngine** -- controls the WMX engine lifecycle (device creation and
communication). Used by ``/wmx/engine/set_device`` on ``wmx_engine_node``.

.. code-block:: text

   # Request
   bool   data      # true = create device, false = close device
   string path      # WMX3 device path (e.g., "/opt/wmx3/")
   string name      # Device name identifier
   ---
   # Response
   bool   success   # true if operation succeeded
   string message   # Human-readable result description

Axis Control
^^^^^^^^^^^^^

**SetAxis** -- generic per-axis control. The meaning of ``data`` depends on
the service using it.

.. code-block:: text

   int32[] index    # Axis indices (e.g., [0, 1, 2, 3, 4, 5])
   int32[] data     # Per-axis values (meaning varies by service)
   ---
   bool   success   # true only if ALL axes succeeded
   string message   # Concatenated per-axis result messages

Used by ``/wmx/axis/set_on`` (1=enable / 0=disable), ``/wmx/axis/clear_alarm``
(data unused), ``/wmx/axis/set_mode`` (0=position / 1=velocity),
``/wmx/axis/set_polarity`` (1=normal / -1=reversed), and ``/wmx/axis/homing``
(data unused).

**SetAxisGearRatio** -- configures the encoder gear ratio per axis. Used by
``/wmx/axis/set_gear_ratio``.

.. code-block:: text

   int32[]   index         # Axis indices
   float64[] numerator     # Gear ratio numerators
   float64[] denominator   # Gear ratio denominators
   ---
   bool   success
   string message

Parameters
^^^^^^^^^^^

**LoadWmxParams** -- load axis parameters from a WMX3 XML file
(``/wmx/params/load``).

.. code-block:: text

   string file_path   # absolute path to the WMX3 XML parameter file
   ---
   bool   success
   string message

**GetWmxParams** -- retrieve active axis parameters as text
(``/wmx/params/get``).

.. code-block:: text

   int32[] index          # axis indices to report
   ---
   bool     success
   string   message
   string[] params_dump   # formatted, human-readable parameter dump

I/O
^^^

**GetIoBit** / **SetIoBit** -- read/write a single digital I/O bit.

.. code-block:: text

   # GetIoBit request          # SetIoBit request
   int32 byte                  int32 byte
   int32 bit                   int32 bit
   ---                         int32 value
   bool   success              ---
   int32  value                bool   success
   string message              string message

**GetIoBytes** / **SetIoBytes** -- read/write a contiguous block of I/O bytes.

.. code-block:: text

   # GetIoBytes request        # SetIoBytes request
   int32 byte                  int32 byte
   int32 length                uint8[] data
   ---                         ---
   bool    success             bool   success
   uint8[] data                string message
   string  message

EtherCAT
^^^^^^^^^

**EcatGetNetworkState** -- full master + per-slave network state.

.. code-block:: text

   int32 master_id
   ---
   bool   success
   string message
   int32  master_state      # 0=None 1=Init 2=Preop 4=Boot 8=Safeop 16=Op
   int32  master_mode
   uint32 comm_period
   uint32 total_axes
   uint32 packet_loss
   uint32 over_cycle
   int32  num_of_slaves
   int32[]  slave_ids
   int32[]  slave_states
   bool[]   slave_offline
   bool[]   slave_inaccessible
   uint32[] slave_vendor_ids
   uint32[] slave_product_codes
   # (plus additional timing and addressing fields)

**EcatRegisterRead** -- read raw register data from a slave.

.. code-block:: text

   int32 master_id
   int32 slave_id
   int32 reg_address   # 0x000–0xFFF
   int32 length        # 1–4096 bytes
   ---
   bool    success
   uint8[] data
   string  message

**EcatResetStatistics** / **EcatStartHotconnect** -- both take only
``int32 master_id`` and return ``bool success`` + ``string message``.

Building the Package
--------------------

This package must be built **before** ``wmx_ros2_package`` because the main
package depends on the generated message headers:

.. code-block:: bash

   cd ~/workspaces/movensys_ws
   colcon build --packages-select wmx_ros2_message
   source install/setup.bash

Verify the interfaces are registered:

.. code-block:: bash

   ros2 interface list | grep wmx

Expected:

.. code-block:: text

   wmx_ros2_message/msg/AxisPose
   wmx_ros2_message/msg/AxisState
   wmx_ros2_message/msg/AxisVelocity
   wmx_ros2_message/srv/EcatGetNetworkState
   wmx_ros2_message/srv/EcatRegisterRead
   wmx_ros2_message/srv/EcatResetStatistics
   wmx_ros2_message/srv/EcatStartHotconnect
   wmx_ros2_message/srv/GetIoBit
   wmx_ros2_message/srv/GetIoBytes
   wmx_ros2_message/srv/GetWmxParams
   wmx_ros2_message/srv/LoadWmxParams
   wmx_ros2_message/srv/SetAxis
   wmx_ros2_message/srv/SetAxisGearRatio
   wmx_ros2_message/srv/SetEngine
   wmx_ros2_message/srv/SetIoBit
   wmx_ros2_message/srv/SetIoBytes

Inspect a specific interface:

.. code-block:: bash

   ros2 interface show wmx_ros2_message/msg/AxisState
