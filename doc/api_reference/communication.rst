Communication Overview
======================

The WMX R2 application uses three communication layers:

- **ROS2 DDS** (CycloneDDS) -- All inter-node communication via topics, services,
  and actions over the ROS2 middleware.
- **WMX API** -- C++ shared libraries at ``/opt/wmx3/`` (``coremotionapi``,
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
   :caption: WMX R2 — three-layer communication architecture
   :zoom:

   %%{init: {"theme": "base", "themeVariables": {"primaryColor": "#1a73e8", "primaryTextColor": "#fff", "primaryBorderColor": "#1558b0", "lineColor": "#555"}}}%%
   flowchart TB
       subgraph L1["Layer 1: ROS2 DDS"]
           direction LR
           N1["wmx_engine_node"]
           N2["wmx_lifecycle_manager_node"]
           N3["wmx_core_motion_node"]
           N4["wmx_io_node"]
           N5["wmx_ethercat_node"]
           N6["joint_state_broadcaster<br/>joint_trajectory_controller<br/>joint_position_controller<br/>gripper_controller<br/>differential_drive_controller"]
       end

       subgraph L2["Layer 2: WMX API"]
           direction LR
           A1["libcoremotionapi<br/>axis status, servo, position &amp; velocity"]
           A2["libadvancedmotionapi<br/>C-spline execution"]
           A3["libioapi<br/>digital I/O"]
           A4["libecapi<br/>EtherCAT diagnostics"]
           A5["libwmx3api<br/>device lifecycle"]
       end

       subgraph L3["Layer 3: EtherCAT"]
           direction LR
           E1["WMX3 motion engine"]
           E2["EtherCAT master"]
           E3["Servo drives, daisy-chained"]
           E4["I/O module<br/>(gripper output bit)"]
       end

       L1 -->|"C++ library calls  (same machine, shared memory)"| L2
       L2 -->|"WMX3 real-time process"| L3
       E1 --> E2 --> E3 & E4

For the full list of ROS2 interfaces, see:

- :doc:`ros2_services` -- engine, lifecycle, axis, I/O, and EtherCAT services
- :doc:`ros2_topics` -- published and subscribed topics
- :doc:`ros2_actions` -- the ``FollowJointTrajectory`` action
- :doc:`wmx_r2_control` -- the ``ros2_control`` route to the same engine
