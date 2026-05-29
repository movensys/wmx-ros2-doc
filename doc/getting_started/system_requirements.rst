System Requirements
===================

Hardware Requirements
---------------------

**Compute Platform:**

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Component
     - Minimum
     - Recommended
   * - CPU
     - x86_64 or ARM64 (aarch64)
     - Intel Core i7 or NVIDIA Jetson Orin/Thor
   * - RAM
     - 4 GB
     - 8 GB or more
   * - Storage
     - 10 GB free
     - 20 GB free (including ROS2 + MoveIt2)
   * - GPU
     - Not required for base operation
     - NVIDIA GPU with CUDA for Isaac cuMotion

WMX Motion Control Engine
--------------------------

The WMX motion control engine is a high-performance, high-accuracy, real-time motion control
platform developed by MOVENSYS. It provides deterministic servo control over
EtherCAT fieldbus and serves as the hardware abstraction layer between ROS2
and physical servo drives.

**Key features:**

- **Real-time EtherCAT master** -- manages cyclic communication with servo
  drives at deterministic update rates
- **Multi-axis coordination** -- supports synchronized motion across 6+ servo
  axes with cubic spline interpolation (``CSplinePos``)
- **Shared-memory architecture** -- multiple ROS2 nodes connect to the same
  WMX engine instance through independent device handles, bridging the
  non-real-time ROS2 domain with the real-time WMX engine
- **Hardware abstraction** -- provides a unified C++ API (``CoreMotion``,
  ``AdvancedMotion``, ``Io``, ``Ecat``, ``WMX3Api``) so ROS2 nodes remain
  robot-agnostic; only configuration files differ between robots

The WMX runtime must be installed at ``/opt/wmx3/`` before building or
running the WMX ROS2 packages. See :doc:`install_wmx3` for verification
steps.

.. note::

   Root (sudo) access is required at runtime. The WMX motion control engine
   and EtherCAT communication require kernel-level access to the network
   interface.

Supported Robot Models and Platforms
------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 15 15 15 55

   * - Model
     - DOF
     - Payload
     - Status
   * - Dobot CR3A
     - 6
     - 16.5 kg
     - Fully supported. Configuration files and WMX parameters included.

The architecture is robot-agnostic for any 6-DOF manipulator with EtherCAT
servo drives. See :doc:`../integration/integration` for details on adapting
to other robots.

.. list-table::
   :header-rows: 1
   :widths: 18 11 22 18 17 14

   * - Platform
     - Architecture
     - Ubuntu Version
     - ROS2 Distro
     - Model
     - Notes
   * - Desktop PC
     - x86_64
     - 22.04 LTS (Jammy) / 24.04 LTS (Noble)
     - `Humble <https://docs.ros.org/en/humble/index.html>`_ / `Jazzy <https://docs.ros.org/en/jazzy/index.html>`_
     - Desktop with NVIDIA RTX 5070 / 5090
     - Simulation and HIL
   * - Intel IPC
     - x86_64
     - 22.04 LTS (Jammy) / 24.04 LTS (Noble)
     - `Humble <https://docs.ros.org/en/humble/index.html>`_ / `Jazzy <https://docs.ros.org/en/jazzy/index.html>`_
     - Advantech UNO-258
     - Edge AI platform
   * - NVIDIA Jetson Orin
     - aarch64
     - 22.04 LTS (Jammy)
     - `Humble <https://docs.ros.org/en/humble/index.html>`_
     - Advantech MIC-713 / MIC-733ao
     - Edge AI platform
   * - NVIDIA Jetson Thor
     - aarch64
     - 24.04 LTS (Noble)
     - `Jazzy <https://docs.ros.org/en/jazzy/index.html>`_
     - Advantech MIC-743
     - Edge AI platform

The C++ standard required is **C++17** (set in ``CMakeLists.txt``).

**EtherCAT Network Interface:**

- **Dedicated Ethernet NIC** for the EtherCAT fieldbus (cannot be shared with
  regular network traffic)
- The EtherCAT port connects directly to the first servo drive in the daisy chain

.. warning::

   The EtherCAT Ethernet port is **not** a standard TCP/IP connection. Do not
   configure it with a regular IP address. The WMX engine controls this
   interface at the raw Ethernet level.

