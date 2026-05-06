WMX ROS2 Documentation
=======================

Overview
----------------------------------------

Welcome to the WMX ROS2 documentation. This project provides ROS2 packages
for controlling various robot platforms through the WMX motion control platform over EtherCAT. 

WMX is a deterministic motion control engine with over a decade of industrial deployment in semicondutor, manufacturing, and  precision robotics. 
It uses Ethercat with deterministic real-time kernel system as the dominant industrial filedbus. 
It has various motion profiling such as PVT (Position-Velocity-Time), multi-axis coordinated motion. 
It can takes irregural axes trajectory points and generate exact cyclic commands at the scan rate.

In this project, wmx-ros2 is a package that wrapped WMX with ROS2 framework. It has common nodes such as joint trajectory controller, joint state broadcaster, etc.

For current and future development, please see :doc:`integration/integration`.


Key capabilities
----------------------------------------

- Follow the :doc:`getting_started/index` guide to set up your environment and get running.
- Browse the :doc:`packages/packages` for ``wmx_ros2_message`` and ``wmx_ros2_package`` details.
- Explore :doc:`integration/integration` for MoveIt2 and Isaac cuMotion planning.
- Check the :doc:`api_reference/api_reference` for ROS2 services, topics, and actions.
- See :doc:`examples/examples` for real-world application demos.
- Scan through :doc:`troubleshooting/troubleshooting` for answers to common issues.


Support
----------------------------------------

If you need professional services related to WMX ROS2, please contact Movensys Inc at https://www.movensys.com/en/company/contact

.. toctree::
   :maxdepth: 3

   getting_started/index
   packages/packages
   integration/integration
   api_reference/api_reference
   examples/examples
   troubleshooting/troubleshooting
   support
   about
