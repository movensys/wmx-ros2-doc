wmx_r2_message
=================

Overview
--------

``wmx_r2_message`` holds every custom interface definition used by WMX R2.
It contains **one message** and **22 services**, and no actions — trajectory
execution uses the standard ``control_msgs/action/FollowJointTrajectory``.

The package builds interfaces only. It has no nodes, no libraries, and no
dependency on the WMX3 SDK, so it can be built and installed on a machine
that has no WMX runtime — which is what lets a planning or application
machine talk to a WMX R2 robot without installing the engine.

.. code-block:: text

   wmx_r2_message/
   ├── msg/
   │   └── AxesStatus.msg
   ├── srv/
   │   ├── SetEngine.srv               # engine
   │   ├── ImportAndSetAll.srv
   │   ├── GetAxisParam.srv
   │   ├── SetNodeState.srv            # lifecycle
   │   ├── GetNodeStates.srv
   │   ├── SetAxes.srv                 # axes
   │   ├── SetAxesGearRatio.srv
   │   ├── StartAxesPose.srv
   │   ├── StartAxesVelocity.srv
   │   ├── GetIoBit.srv                # I/O
   │   ├── GetIoBits.srv
   │   ├── GetIoByte.srv
   │   ├── GetIoBytes.srv
   │   ├── SetIoBit.srv
   │   ├── SetIoBits.srv
   │   ├── SetIoByte.srv
   │   ├── SetIoBytes.srv
   │   ├── EcatGetMasterInfo.srv       # EtherCAT
   │   ├── EcatRegisterRead.srv
   │   ├── EcatResetStatistics.srv
   │   ├── EcatScanNetwork.srv
   │   └── EcatStartHotconnect.srv
   ├── test/
   ├── CMakeLists.txt
   └── package.xml

Conventions
-----------

Every service response carries ``bool success`` and ``string message``.

- On the **array** services, ``success`` is true only when *every* entry
  succeeded. ``message`` concatenates the per-entry results, so read it even
  when ``success`` is false — it says which axis failed and why.
- ``axis`` is a WMX3 axis index. All parallel arrays in one request must be
  the same length.
- I/O ``addr`` is a byte address; ``bit`` is the index inside that byte,
  0–7. All values are decimal.

Dependencies
------------

.. code-block:: xml

   <buildtool_depend>ament_cmake</buildtool_depend>
   <build_depend>rosidl_default_generators</build_depend>
   <depend>std_msgs</depend>
   <exec_depend>rosidl_default_runtime</exec_depend>
   <member_of_group>rosidl_interface_packages</member_of_group>

``std_msgs`` is needed only for the ``Header`` in ``AxesStatus``.

Message definitions
-------------------

AxesStatus
^^^^^^^^^^

The only custom message. Published on ``/wmx/axes/status`` by
``wmx_core_motion_node`` at ``axes_status_rate`` (default 100 Hz).

.. code-block:: text

   std_msgs/Header header

   bool[] amp_alarm         # amplifier alarm active
   bool[] servo_on          # servo power on
   bool[] home_done         # homing completed
   bool[] home_switch       # home switch input
   bool[] negative_ls       # negative limit switch
   bool[] positive_ls       # positive limit switch
   bool[] motion_complete   # engine reports the move finished

   float64[] pos_cmd         # commanded position
   float64[] velocity_cmd    # commanded velocity
   float64[] actual_pos      # encoder position
   float64[] actual_velocity # encoder velocity
   float64[] actual_torque   # torque feedback

All arrays are parallel and indexed by axis. ``pos_cmd`` minus
``actual_pos`` is the following error.

Service definitions
-------------------

Engine
^^^^^^

**ImportAndSetAll** — imports a WMX3 parameter XML into the running engine.

.. code-block:: text

   string path       # absolute path to the WMX3 XML parameter file
   ---
   bool success
   string message

**GetAxisParam** — dumps the active gear ratio, polarity, and command mode.

.. code-block:: text

   int32[] axis          # axis index per entry
   ---
   bool success
   string message
   string[] axis_param   # one formatted, human-readable string per axis

**SetEngine** — defined and unit-tested, but **not currently served by any
node**. ``wmx_engine_node`` uses ``std_srvs/srv/SetBool`` on
``/wmx/engine/set_engine`` instead. It is kept for compatibility with
external tools built against earlier releases.

.. code-block:: text

   bool data         # engine start or stop
   string path       # WMX path
   string name       # device name
   ---
   bool success
   string message

Lifecycle
^^^^^^^^^

**SetNodeState** — drives one lifecycle node, or every node found.

.. code-block:: text

   string node_name   # empty applies the transition to every lifecycle node found
   string transition  # configure | activate | deactivate | cleanup
                      # shutdown | bringup | bringdown
   ---
   bool success
   string message
   string[] node_names
   string[] states

**GetNodeStates** — lists every lifecycle node with its current state.

.. code-block:: text

   ---
   bool success
   string message
   string[] node_names   # every lifecycle node found, in bring-up order
   string[] states       # lifecycle state per entry

Axes
^^^^

**SetAxes** — the workhorse. Used by ``set_servo_on``, ``clear_amp_alarm``,
``set_axis_command_mode``, ``set_axis_polarity``, ``start_home``, and
``stop``. The meaning of ``data`` depends on the service; several ignore it.

.. code-block:: text

   int32[] axis      # axis index per entry
   int32[] data      # per-axis value; see the service
   ---
   bool success
   string message

**SetAxesGearRatio** — encoder counts to user units, per axis.

.. code-block:: text

   int32[] axis
   float64[] numerator      # encoder counts
   float64[] denominator    # user units
   ---
   bool success
   string message

**StartAxesPose** — absolute (``start_pos``) and relative (``start_mov``)
moves.

.. code-block:: text

   int32[] axis
   float64[] target      # target position per axis
   float64[] velocity
   float64[] acc
   float64[] dec
   ---
   bool success
   string message

**StartAxesVelocity** — constant-velocity (``start_vel``) and jog
(``start_jog``) motion. The sign of ``velocity`` selects the direction.

.. code-block:: text

   int32[] axis
   float64[] velocity
   float64[] acc
   float64[] dec
   ---
   bool success
   string message

I/O
^^^

.. list-table::
   :header-rows: 1
   :widths: 24 20 56

   * - Service
     - Shape
     - Used by
   * - ``GetIoBit``
     - scalar
     - ``get_in_bit``, ``get_out_bit``
   * - ``GetIoBits``
     - array
     - ``get_in_bits``, ``get_out_bits``
   * - ``GetIoByte``
     - scalar
     - ``get_in_byte``, ``get_out_byte``
   * - ``GetIoBytes``
     - range
     - ``get_in_bytes``, ``get_out_bytes``
   * - ``SetIoBit``
     - scalar
     - ``set_out_bit``
   * - ``SetIoBits``
     - array
     - ``set_out_bits``
   * - ``SetIoByte``
     - scalar
     - ``set_out_byte``
   * - ``SetIoBytes``
     - range
     - ``set_out_bytes``

.. code-block:: text

   # GetIoBit                          # GetIoBits (scattered)
   int32 addr                          int32[] addr
   int32 bit    # 0-7                  int32[] bit
   ---                                 ---
   bool success                        bool success   # true only if every entry read
   uint8 data   # 0 or 1               uint8[] data
   string message                      string message

   # GetIoByte                         # GetIoBytes (consecutive)
   int32 addr                          int32 addr     # starting address
   ---                                 int32 size     # number of bytes, > 0
   bool success                        ---
   uint8 data   # 0-255                bool success
   string message                      uint8[] data
                                       string message

   # SetIoBit                          # SetIoBits (scattered)
   int32 addr                          int32[] addr
   int32 bit                           int32[] bit
   uint8 data   # 0 or 1               uint8[] data
   ---                                 ---
   bool success                        bool success
   string message                      string message

   # SetIoByte                         # SetIoBytes (consecutive)
   int32 addr                          int32 addr     # starting address
   uint8 data   # 0-255                uint8[] data
   ---                                 ---
   bool success                        bool success
   string message                      string message

The ``Bits`` and ``Bytes`` variants write in a single SDK call, so scattered
outputs change together rather than one at a time.

EtherCAT
^^^^^^^^

``EcatResetStatistics``, ``EcatScanNetwork``, and ``EcatStartHotconnect``
share the same shape:

.. code-block:: text

   int32 master_id
   ---
   bool success
   string message

**EcatRegisterRead** — reads a slave ESC register.

.. code-block:: text

   int32 master_id
   int32 slave_id
   int32 reg_addr    # valid range 0x000 - 0xFFF
   int32 len         # valid range 1 - 4096 bytes
   ---
   bool success
   uint8[] data
   string message

**EcatGetMasterInfo** — the full network picture in one call: master state
and timing counters, plus one entry per slave in the parallel ``slave_*``
arrays.

.. code-block:: text

   int32 master_id
   ---
   bool success
   string message

   # master
   int32 state         # 0=None 1=Init 2=Preop 4=Boot 8=Safeop 16=Op
   int32 mode          # 0=Cyclic 1=PP 2=Monitor
   uint32 comm_period
   uint32 total_axes_num
   uint32 total_input_size
   uint32 total_output_size
   uint32 ring_num
   uint32 total_rx_pdo_size
   uint32 total_tx_pdo_size
   uint32 tx_delay
   uint32 min_tx_delay
   uint32 max_tx_delay
   uint32 packet_loss
   uint32 packet_timeout
   uint32 over_cycle

   # slaves (parallel arrays, one entry per slave)
   int32 num_of_slaves
   int32[]  slave_ids
   int32[]  slave_states
   int32[]  slave_al_status_codes
   int32[]  slave_positions
   int32[]  slave_addresses
   bool[]   slave_offline
   bool[]   slave_inaccessible
   bool[]   slave_new_slaves
   bool[]   slave_reverse_slaves
   uint32[] slave_vendor_ids
   uint32[] slave_product_codes
   uint32[] slave_revision_nos
   uint32[] slave_serial_nos
   uint32[] slave_aliases
   int32[]  slave_input_addrs
   int32[]  slave_input_sizes
   int32[]  slave_output_addrs
   int32[]  slave_output_sizes
   int32[]  slave_num_of_axes

A slave stuck below ``Op`` with a non-zero ``slave_al_status_codes`` entry
is the usual EtherCAT failure. See
:doc:`../troubleshooting/troubleshooting`.

Building the package
--------------------

Build the messages before anything that depends on them:

.. code-block:: bash

   wros colcon build --packages-select wmx_r2_message
   wros colcon build

Verify the generated interfaces:

.. code-block:: bash

   wros ros2 interface list | grep wmx_r2_message
   wros ros2 interface show wmx_r2_message/msg/AxesStatus
   wros ros2 interface show wmx_r2_message/srv/SetAxes

See also
--------

- :doc:`ros2_services` -- what each service does, with call examples
- :doc:`ros2_topics` -- ``AxesStatus`` in context
- :doc:`wmx_r2_package` -- the nodes that serve these interfaces
