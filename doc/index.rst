WMX ROS2 Documentation
=======================

Overview
----------------------------------------

:red:`opening`
Welcome to the WMX ROS2 documentation. This project provides ROS2 packages
for controlling various robot platforms through the WMX motion control platform over EtherCAT. 

:red:`what is problem`
may robotics hard to go to industrial application due to requirement for deterministic 

What is wmx-ros2
----------------------------------------

:red:`what is wmx-ros2`
In this project, wmx-ros2 is a package that wrapped WMX with ROS2 framework. It has common nodes such as joint trajectory controller, joint state broadcaster, etc.
It provides simulation, hardware in loop and real world deployment. 

:red:`what is wmx`
WMX is a deterministic motion control engine with over a decade of industrial deployment in semicondutor, manufacturing, and  precision robotics. 
It uses Ethercat with deterministic real-time kernel system as the dominant industrial filedbus. 
It has various motion profiling such as PVT (Position-Velocity-Time), multi-axis coordinated motion. 
It can takes irregural axes trajectory points and generate exact cyclic commands at the scan rate. 
It has free trial every 6 hours, only need to restart the engine.







Key capabilities
----------------------------------------

- Follow the :doc:`getting_started/index` guide to set up your environment and get running.
- Explore :doc:`integration/integration` for current and future integration scenarios.
- Check the :doc:`api_reference/api_reference` for ROS2 services, topics, and actions.
- Scan through :doc:`support` for answers to common issues. 







.. toctree::
   :maxdepth: 3

   getting_started/index
   integration/integration
   api_reference/api_reference
   support
   about