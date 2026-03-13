System Requirements
===================

WMX Motion Control Engine
--------------------------

The WMX motion control engine is a high-performance, real-time motion control
platform developed by MOVENSYS. It provides deterministic servo control over
EtherCAT fieldbus and serves as the hardware abstraction layer between ROS2
and physical servo drives.

**Key features:**

- **Real-time EtherCAT master** -- manages cyclic communication with servo
  drives at deterministic update rates
- **Multi-axis coordination** -- supports synchronized motion across 6+ axes
  with cubic spline interpolation (``CSplinePos``)
- **Shared-memory architecture** -- multiple ROS2 nodes connect to the same
  WMX engine instance through independent device handles, enabling concurrent
  state reading and command execution
- **Hardware abstraction** -- provides a unified C++ API (``CoreMotion``,
  ``AdvancedMotion``, ``Io``, ``Ecat``, ``WMX3Api``) so ROS2 nodes remain
  robot-agnostic; only configuration files differ between robots

The WMX runtime (LMX) must be installed at ``/opt/lmx/`` before building or
running the WMX ROS2 packages. See :doc:`install_dependencies` for verification
steps.

Operating System
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - OS
     - Version
     - Notes
   * - Ubuntu
     - 22.04 LTS (Jammy)
     - Primary development and testing platform
   * - Ubuntu
     - 24.04 LTS (Noble)
     - Supported with ROS2 Jazzy

.. note::

   Root (sudo) access is required at runtime. The WMX motion control engine
   and EtherCAT communication require kernel-level access to the network
   interface.

ROS2 Distribution
-----------------

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Distribution
     - Ubuntu Version
     - Platform
   * - ROS2 Humble Hawksbill
     - Ubuntu 22.04
     - NVIDIA Jetson Orin, Intel x86_64
   * - ROS2 Jazzy Jalisco
     - Ubuntu 24.04
     - Intel x86_64

The C++ standard required is **C++17** (set in ``CMakeLists.txt``).

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
     - Intel Core i7 or NVIDIA Jetson Orin
   * - RAM
     - 4 GB
     - 8 GB or more
   * - Storage
     - 10 GB free
     - 20 GB free (including ROS2 + MoveIt2)
   * - GPU
     - Not required for base operation
     - NVIDIA GPU with CUDA for Isaac cuMotion

**Tested Platforms:**

- **Intel x86_64** -- Desktop/industrial PC (referenced as ``mvsk`` in configs)
- **NVIDIA Jetson Orin** -- Edge AI platform (referenced as ``mic-733ao`` in configs)

**EtherCAT Network Interface:**

- **Dedicated Ethernet NIC** for the EtherCAT fieldbus (cannot be shared with
  regular network traffic)
- The EtherCAT port connects directly to the first servo drive in the daisy chain

.. warning::

   The EtherCAT Ethernet port is **not** a standard TCP/IP connection. Do not
   configure it with a regular IP address. The WMX engine controls this
   interface at the raw Ethernet level.

**Supported Robot:**

- **Dobot CR3A** -- 6-DOF collaborative robot with EtherCAT servo drives and
  pneumatic gripper

The architecture is robot-agnostic for any 6-DOF manipulator with EtherCAT
servo drives. See :doc:`../packages/wmx_ros2_package` for details on adapting
to other robots.

Supported Models & Platforms
----------------------------

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

.. list-table::
   :header-rows: 1
   :widths: 30 25 25 20

   * - Platform
     - Architecture
     - ROS2 Distro
     - Config File
   * - Intel x86_64 PC
     - x86_64
     - Humble / Jazzy
     - ``intel_manipulator_config_cr3a.yaml``
   * - NVIDIA Jetson Orin
     - aarch64
     - Humble
     - ``orin_manipulator_config_cr3a.yaml``
