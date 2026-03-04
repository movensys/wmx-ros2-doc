Communication Overview
======================

The WMX ROS2 application uses three communication layers:

- **ROS2 DDS** (CycloneDDS) -- All inter-node communication via topics, services,
  and actions over the ROS2 middleware.
- **WMX API** -- C++ shared libraries at ``/opt/lmx/`` (``coremotionapi``,
  ``advancedmotionapi``, ``ioapi``, ``ecapi``, ``wmx3api``) that bridge ROS2
  nodes to the motion engine via shared memory.
- **EtherCAT** -- Real-time fieldbus managed by the WMX engine for deterministic,
  low-latency servo drive communication.

.. note::

   The system does **not** use TCP/IP to communicate with the robot controller.
   The WMX motion engine runs on the same machine as the ROS2 nodes and
   communicates with servo drives over EtherCAT.

For the full list of ROS2 interfaces, see:

- :doc:`../api_reference/ros2_topics` -- Published and subscribed topics
- :doc:`../api_reference/ros2_services` -- Engine, axis, I/O, and EtherCAT services
- :doc:`../api_reference/ros2_actions` -- FollowJointTrajectory action
