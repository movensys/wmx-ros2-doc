The WMX3 API Underneath WMX R2
==============================

Every ROS 2 service on the preceding pages is a thin wrapper over a call into
the **WMX3 API** — the C++ SDK that ships with the WMX Runtime. When a service
answers ``success: false`` with an error code, that code is the engine's, and
its meaning is documented in the SDK reference rather than anywhere in WMX R2.

This page says where that reference is and how the two layers line up.

Where the reference lives
-------------------------

The WMX Runtime installs both of its manuals under ``/opt/wmx3/Doc/Web/``:

.. code-block:: text

   /opt/wmx3/Doc/Web/
   ├── API/API_UserManual.zip           the WMX3 API reference
   ├── Application/App_UserManual.zip   the WMX web tools user guide
   ├── certs/
   └── logs/

``certs/`` and ``logs/`` belong to the gateway that serves them; the content is
the two archives. Both are also reachable as the **WMX API Manual** and
**WMX App Manual** tiles on the WMX Home dashboard when the gateway is running
— see :doc:`../try_your_robot/wmx_web_tools`.

To read the API manual from disk, unpack it and open the English entry point:

.. code-block:: bash

   mkdir -p ~/wmx3-api-manual
   unzip /opt/wmx3/Doc/Web/API/API_UserManual.zip -d ~/wmx3-api-manual
   xdg-open ~/wmx3-api-manual/en/api-reference/index.html

.. note::

   The API archive is about 90 MB unpacked, and carries ``en``, ``jp``, and
   ``kr`` trees. The application manual is far smaller. Unpack only the
   language you need if space matters:
   ``unzip ... 'en/*' -d ~/wmx3-api-manual``.

What is in the API manual
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Part
     - Contents
   * - ``en/api-reference/``
     - The API reference proper — functions grouped by module.
   * - ``en/api/html/``
     - The generated class documentation for the ``wmx3_api`` namespace:
       every class, its members, and the error-code enumerations.
   * - ``en/guide/general/``
     - How the engine is put together — device architecture, the console,
       servo-on and communication sequences, and function notes.
   * - ``en/guide/ec/``
     - The EtherCAT chapter: AL states, distributed clocks, hot connect,
       cyclic modes, the object dictionary, logging, and **the ENI file**.
   * - ``en/guide/.../cpp_vs_net/``
     - Differences between the C++ and .NET bindings. WMX R2 uses C++.

The SDK headers themselves are in ``/opt/wmx3/include/`` and are the fastest
way to check a signature: ``WMX3Api.h`` (device lifecycle),
``CoreMotionApi.h`` (axes and motion), ``IOApi.h``, ``EcApi.h`` (EtherCAT),
plus the advanced-motion, compensation, buffer, event, log, and user-memory
modules.

How WMX R2 maps onto it
-----------------------

The nodes in ``wmx_r2_package`` each own one SDK module, which is why the
ROS 2 namespaces are shaped the way they are.

.. list-table::
   :header-rows: 1
   :widths: 32 32 36

   * - WMX R2 node
     - ROS 2 namespace
     - WMX3 API
   * - ``wmx_engine_node``
     - ``/wmx/engine/``
     - ``WMX3Api`` — ``CreateDevice``, ``StartCommunication``,
       ``Config::ImportAndSetAll``
   * - ``wmx_core_motion_node``
     - ``/wmx/axes/``
     - ``CoreMotion`` — ``Motion::StartPos``, ``StartMov``, ``StartJog``,
       ``Home::StartHome``, ``AxisControl::SetServoOn``
   * - ``wmx_io_node``
     - ``/wmx/io/``
     - ``Io`` — bit and byte input and output
   * - ``wmx_ethercat_node``
     - ``/wmx/ecat/``
     - ``Ecat`` — master info, register access, network scan, hot connect
   * - ``wmx_r2_control``
     - ``ros2_control``
     - The same ``CoreMotion`` calls, driven by a controller manager instead
       of by services

.. tip::

   Two places where going to the SDK reference is usually faster than
   guessing:

   - **An unfamiliar error code.** ``wmx_engine_node`` logs the numeric code
     and its string; the enumerations in ``en/api/html/`` say what
     provokes it. ``CreateDeviceLockError`` on startup, for example, means
     something else already holds the device.
   - **Exact units and profile semantics.** ``acc`` and ``dec`` are
     accelerations on the ROS 2 wire but become ramp times inside the
     time-based profile the engine uses — the kind of detail that only the
     SDK documentation states.

.. warning::

   The WMX3 API is the vendor's interface and changes on its own release
   schedule. Check the version the manual was built for against the
   ``WMX`` version in the gateway's status bar before relying on a detail;
   this install reports ``WMX 3.7.0.0``.
