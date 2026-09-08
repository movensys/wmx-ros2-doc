Integration Scenarios
=====================

WMX R2 supports motion-planning backends for both robot arms (MoveIt2, Isaac
cuMotion) and mobile bases (Nav2), and can be extended with custom planners and
standalone applications.

.. rubric:: Planning Backend Selection

Use the decision tree below to find the right integration for your use case,
then follow the corresponding guide.

.. mermaid::
   :caption: Integration — which scenario fits your use case?
   :zoom:

   %%{init: {"theme": "base", "themeVariables": {"primaryColor": "#2563eb", "primaryTextColor": "#0f172a", "primaryBorderColor": "#1e40af", "lineColor": "#475569", "fontSize": "14px", "edgeLabelBackground": "#f1f5f9", "tertiaryColor": "#f1f5f9"}}}%%
   flowchart TD
       START([" What do I need? "])

       Q0{{"Robot arm or<br/>mobile base?"}}
       Q1{{"NVIDIA GPU with<br/>CUDA available?"}}
       Q2{{"Need vision / 3D<br/>obstacle avoidance?"}}
       Q3{{"Custom planning<br/>algorithm?"}}
       Q4{{"Standalone<br/>ROS2 app?"}}

       R_NAV["**Nav2**<br/><br/>Mobile base<br/>Path planning · AMCL"]
       R_MV["**MoveIt2**<br/><br/>OMPL · CHOMP · Pilz<br/>Any hardware"]
       R_CU["**Isaac cuMotion**<br/><br/>GPU-accelerated<br/>AprilTag · NvBlox"]
       R_CP["**Custom Planner**<br/><br/>Your own algorithm<br/>MoveIt2 plugin API"]
       R_CA["**Custom App**<br/><br/>WMX services direct<br/>No MoveIt2 needed"]

       START --> Q0
       Q0 -->|"Mobile base"| R_NAV
       Q0 -->|"Robot arm"| Q1

       Q1 -->|"Yes"| Q2
       Q1 -->|"No"| Q3

       Q2 -->|"Yes"| R_CU
       Q2 -->|"No"| R_MV

       Q3 -->|"Yes"| R_CP
       Q3 -->|"No"| Q4

       Q4 -->|"Yes"| R_CA
       Q4 -->|"No"| R_MV

       classDef startNode fill:#0f172a,stroke:#334155,stroke-width:3px,color:#fff,font-weight:bold
       classDef question fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a5f,font-weight:bold
       classDef moveit fill:#16a34a,stroke:#15803d,stroke-width:2px,color:#fff
       classDef cumotion fill:#2563eb,stroke:#1d4ed8,stroke-width:2px,color:#fff
       classDef custom fill:#ea580c,stroke:#c2410c,stroke-width:2px,color:#fff
       classDef customapp fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff
       classDef nav fill:#0d9488,stroke:#0f766e,stroke-width:2px,color:#fff

       class START startNode
       class Q0,Q1,Q2,Q3,Q4 question
       class R_NAV nav
       class R_MV moveit
       class R_CU cumotion
       class R_CP custom
       class R_CA customapp

       linkStyle 0 stroke:#475569,stroke-width:2px
       linkStyle 1 stroke:#0d9488,stroke-width:2px
       linkStyle 2 stroke:#475569,stroke-width:2px
       linkStyle 3 stroke:#16a34a,stroke-width:2px
       linkStyle 4 stroke:#ef4444,stroke-width:2px
       linkStyle 5 stroke:#16a34a,stroke-width:2px
       linkStyle 6 stroke:#ef4444,stroke-width:2px
       linkStyle 7 stroke:#16a34a,stroke-width:2px
       linkStyle 8 stroke:#ef4444,stroke-width:2px
       linkStyle 9 stroke:#16a34a,stroke-width:2px
       linkStyle 10 stroke:#ef4444,stroke-width:2px

Available integrations:

- **MoveIt2** -- Standard ROS2 motion planning via ``FollowJointTrajectory``
- **Isaac cuMotion** -- NVIDIA GPU-accelerated collision-aware planning
- **Nav2** -- ROS2 navigation for differential-drive mobile bases, executed on
  the wheels via ``/cmd_vel_safe``
- **Custom Planner** -- Integrate your own planning algorithm
- **Custom Application** -- Build standalone ROS2 apps using WMX services
- **Natural-Language and Vision Control** -- drive the robot with a VLM/LLM
  through a FastAPI service (an application layer on top of MoveIt2)

Either arm route can also run through ``ros2_control``: the
``wmx_r2_control/WmxSystemHardware`` plugin exposes WMX3 axes to the standard
``controller_manager``. See :doc:`../api_reference/wmx_r2_control`.

.. toctree::
   :maxdepth: 2

   moveit2_integration
   cumotion_integration
   nav2_integration
   custom_planner
   custom_application
   intelligence_integration
