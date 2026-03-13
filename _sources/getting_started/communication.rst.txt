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

The diagram below shows how the three layers stack and which libraries and buses connect them:

.. mermaid::
   :caption: WMX ROS2 — three-layer communication architecture
   :zoom:

   %%{init: {"theme": "base", "themeVariables": {"primaryColor": "#1a73e8", "primaryTextColor": "#fff", "primaryBorderColor": "#1558b0", "lineColor": "#555"}}}%%
   flowchart TB
       subgraph L1["Layer 1 — ROS2 DDS  (CycloneDDS middleware)"]
           direction LR
           N1["manipulator_state"]
           N2["follow_joint_trajectory_server"]
           N3["wmx_engine_node"]
           N4["wmx_core_motion_node"]
           N5["wmx_io_node"]
           N6["wmx_ethercat_node"]
       end

       subgraph L2["Layer 2 — WMX API  (C++ shared libraries at /opt/lmx/)"]
           direction LR
           A1["libcoremotionapi<br/>Axis position & velocity"]
           A2["libadvancedmotionapi<br/>Cubic spline execution"]
           A3["libioapi<br/>Digital I/O"]
           A4["libecapi<br/>EtherCAT diagnostics"]
           A5["libwmx3api<br/>Device lifecycle"]
       end

       subgraph L3["Layer 3 — EtherCAT  (real-time fieldbus, dedicated NIC)"]
           direction LR
           E1["WMX3 Motion Engine"]
           E2["EtherCAT Master"]
           E3["Servo Drives  J1 → J2 → ... → J6  (daisy-chained)"]
           E4["I/O Module  (gripper digital output)"]
       end

       L1 -->|"C++ library calls  (same machine, shared memory)"| L2
       L2 -->|"WMX3 real-time process"| L3
       E1 --> E2 --> E3 & E4

For the full list of ROS2 interfaces, see:

- :doc:`../api_reference/ros2_topics` -- Published and subscribed topics
- :doc:`../api_reference/ros2_services` -- Engine, axis, I/O, and EtherCAT services
- :doc:`../api_reference/ros2_actions` -- FollowJointTrajectory action
