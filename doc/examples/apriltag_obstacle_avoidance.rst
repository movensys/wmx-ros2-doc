AprilTag + Obstacle Avoidance
=============================

Combines AprilTag-driven pick-and-place with Nvblox obstacle avoidance: Isaac
cuMotion plans collision-free motion against a live Nvblox reconstruction while
Isaac ROS AprilTag locates the target. See :doc:`examples` for the shared
manipulator setup. All commands run through ``mros``.

Simulation
----------

1. Open the Isaac Sim scene:
   ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/7a_apriltag_obstacle_avoidance_simulation.usd``

2. Run the simulator bridge:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py \
           simulator:=isaacsim use_sim_time:=true

3. Launch cuMotion + Nvblox:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_nvblox.launch.py use_sim_time:=true

4. Launch Isaac AprilTag:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_isaac_ros_config isaac_apriltag.launch.py use_sim_time:=true

5. Run AprilTag pick-and-place with obstacle avoidance:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config apriltag_pick_and_place.launch.py \
           use_sim_time:=true target_spawn:=false

HIL
---

1. Open the Isaac Sim scene:
   ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/7b_apriltag_obstacle_avoidance_hil.usd``

2. Start WMX ROS2 for the manipulator (real WMX runtime) with
   ``use_sim_time:=true``.

3. Launch cuMotion + Nvblox:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_nvblox.launch.py use_sim_time:=true

4. Launch Isaac AprilTag:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_isaac_ros_config isaac_apriltag.launch.py use_sim_time:=true

5. Run AprilTag pick-and-place with obstacle avoidance:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config apriltag_pick_and_place.launch.py \
           use_sim_time:=true target_spawn:=false

Real
----

1. Open the Isaac Sim scene:
   ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/7c_apriltag_obstacle_avoidance_real.usd``

2. Start WMX ROS2 for the manipulator on the robot (no ``use_sim_time``).

3. Launch cuMotion + Nvblox:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_nvblox.launch.py

4. Launch Isaac AprilTag:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_isaac_ros_config isaac_apriltag.launch.py

5. Run AprilTag pick-and-place with obstacle avoidance:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config apriltag_pick_and_place.launch.py \
           use_sim_time:=false target_spawn:=true
