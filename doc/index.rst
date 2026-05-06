WMX ROS2 Documentation
=======================

Overview
----------------------------------------

:red:`opening`
Welcome to the WMX ROS2 documentation. This project provides ROS2 packages
for controlling various robot platforms through the WMX motion control platform over EtherCAT. 

:red:`what is problem`

:red:`what is wmx-ros2`
In this project, wmx-ros2 is a package that wrapped WMX with ROS2 framework. It has common nodes such as joint trajectory controller, joint state broadcaster, etc.

:red:`what is wmx`
WMX is a deterministic motion control engine with over a decade of industrial deployment in semicondutor, manufacturing, and  precision robotics. 
It uses Ethercat with deterministic real-time kernel system as the dominant industrial filedbus. 
It has various motion profiling such as PVT (Position-Velocity-Time), multi-axis coordinated motion. 
It can takes irregural axes trajectory points and generate exact cyclic commands at the scan rate.







Key capabilities
----------------------------------------

- Follow the :doc:`getting_started/index` guide to set up your environment and get running.
- Explore :doc:`integration/integration` for current and future integration scenarios.
- Check the :doc:`api_reference/api_reference` for ROS2 services, topics, and actions.
- Scan through :doc:`troubleshooting/troubleshooting` for answers to common issues. 

- Browse the :doc:`packages/packages` for ``wmx_ros2_message`` and ``wmx_ros2_package`` details. :red:`no need`
- See :doc:`examples/examples` for real-world application demos. :red:`combine with integration`





Support
----------------------------------------

If you need professional services related to WMX ROS2, please contact Movensys Inc at https://www.movensys.com/en/company/contact

.. toctree::
   :maxdepth: 3

   getting_started/index
   integration/integration
   api_reference/api_reference
   troubleshooting/troubleshooting
   support
   about

   packages/packages
   examples/examples
   