Testing WMX ROS2
================

Once WMX ROS2 is installed and built, you can validate it in two ways: in
simulation (no physical hardware required) or against real EtherCAT hardware.
Start with simulation to verify basic behavior, then move to real hardware.

The WMX ROS2 nodes communicate directly with the WMX engine over EtherCAT —
there is no built-in mock hardware mode. The mode is selected in
``/opt/wmx3/Module.ini`` by enabling either the simulation or the EtherCAT
platform. Select your mode below, then continue with the common test steps
that follow.

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

      - The WMX ROS2 workspace is built and sourced
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

Test the WMX ROS2 General Nodes (Standalone)
--------------------------------------------------------

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
     ros2 launch wmx_ros2_package wmx_ros2_general_nodes.launch.py"

Startup Sequence
----------------

When launched, four nodes initialize in parallel:

1. **Device creation** -- Each node creates a WMX device handle
2. **EtherCAT scan** -- Network scan discovers all servo drives
3. **Communication start** -- Real-time EtherCAT communication begins
4. **Parameter loading** -- Gear ratios and axis polarities loaded from XML
5. **Servo enable** -- All 6 joint servos cleared and enabled
6. **Ready** -- All nodes report ready

Testing WMX ROS2 Services and Topics
------------------------------------

The general nodes expose the WMX engine, axis, I/O, and EtherCAT control
interfaces as ROS2 services and topics. List what is available and confirm the
engine is communicating:

.. code-block:: bash

   ros2 service list | grep /wmx                                  # Available WMX services
   ros2 topic list | grep /wmx                                    # Available WMX topics
   ros2 service call /wmx/engine/get_status std_srvs/srv/Trigger  # Expect: "Communicating"
   ros2 service call /wmx/ecat/get_network_state \
        wmx_ros2_message/srv/EcatGetNetworkState                  # EtherCAT master/slave status

For the complete list of services, topics, and message types exposed by the
general nodes — engine control, axis motion, I/O, and EtherCAT — see the
`WMX ROS2 General Nodes reference
<https://github.com/movensys/wmx-ros2/blob/release/release-0.2-rc1/doc/reference_wmx_ros2_general_nodes.md>`_.

Shutdown
--------

Press ``Ctrl+C`` in the launch terminal. The nodes will automatically disable
servos, stop EtherCAT communication, and close the WMX device.
