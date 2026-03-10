Getting Started
===============

This guide walks you through the complete setup — from system requirements to
launching your first robot control session with WMX ROS2.

Follow the steps in order. At step 6 choose the path that matches your setup
(simulation or physical robot).

.. mermaid::
   :caption: Getting Started — step-by-step flow
   :zoom:

   %%{init: {"theme": "base", "themeVariables": {"primaryColor": "#1a73e8", "primaryTextColor": "#fff", "primaryBorderColor": "#1558b0", "lineColor": "#1a73e8"}}}%%
   flowchart TB
       S1["1 System<br/>Requirements"]
       S2["2 Install<br/>ROS2"]
       S3["3 Install<br/>Dependencies"]
       S4["4 Create<br/>Workspace"]
       S5["5 Configure<br/>Environment"]
       S6{{"Hardware<br/>path?"}}
       S7["6a Simulation<br/>Hardware"]
       S8["6b Physical<br/>Hardware"]
       S9["7 Communication<br/>Overview"]

       S1 --> S2 --> S3 --> S4 --> S5 --> S6
       S6 -->|"No robot yet"| S7
       S6 -->|"Real robot"| S8
       S7 --> S9
       S8 --> S9

       style S1 fill:#1a73e8,color:#fff
       style S2 fill:#1a73e8,color:#fff
       style S3 fill:#1a73e8,color:#fff
       style S4 fill:#1a73e8,color:#fff
       style S5 fill:#1a73e8,color:#fff
       style S7 fill:#34a853,color:#fff
       style S8 fill:#ea4335,color:#fff
       style S9 fill:#555,color:#fff
       style S6 fill:#fbbc04,color:#000

.. container:: on-this-page

   **On this page**

   .. container:: on-this-page__links

      | :doc:`system_requirements`
      | :doc:`install_ros2`
      | :doc:`install_dependencies`
      | :doc:`create_workspace`
      | :doc:`configure_environment`
      | :doc:`simulation_hardware`
      | :doc:`physical_hardware`
      | :doc:`communication`

.. toctree::
   :maxdepth: 1
   :hidden:

   system_requirements
   install_ros2
   install_dependencies
   create_workspace
   configure_environment
   simulation_hardware
   physical_hardware
   communication
