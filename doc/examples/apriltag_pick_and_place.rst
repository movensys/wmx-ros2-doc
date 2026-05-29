AprilTag Pick-and-Place
=======================

Detect an AprilTag-marked object and pick and place it. Detection uses either
OpenCV AprilTag (with MoveIt2 OMPL) or Isaac ROS AprilTag (with cuMotion). See
:doc:`examples` for the shared manipulator setup. All commands run through
``mros``.

Simulation
----------

1. Open the Isaac Sim scene:
   ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/4a_apriltag_pick_and_place_simulation.usd``

2. Run the simulator bridge:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py \
           simulator:=isaacsim use_sim_time:=true

3. Launch the planner and AprilTag detector:

   .. tab-set::

      .. tab-item:: MoveIt2 OMPL + OpenCV AprilTag
         :sync: ompl

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_perception apriltag_detector.launch.py use_sim_time:=true

      .. tab-item:: cuMotion + Isaac AprilTag
         :sync: cumotion

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_apriltag.launch.py use_sim_time:=true

4. Run the pick-and-place:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config apriltag_pick_and_place.launch.py \
           use_sim_time:=true target_spawn:=false

HIL
---

1. Open the Isaac Sim scene:
   ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/4b_apriltag_pick_and_place_hil.usd``

2. Start WMX ROS2 for the manipulator (real WMX runtime) with
   ``use_sim_time:=true``.

3. Launch the planner and AprilTag detector (with ``use_sim_time:=true``):

   .. tab-set::

      .. tab-item:: MoveIt2 OMPL + OpenCV AprilTag
         :sync: ompl

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_perception apriltag_detector.launch.py use_sim_time:=true

      .. tab-item:: cuMotion + Isaac AprilTag
         :sync: cumotion

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_apriltag.launch.py use_sim_time:=true

4. Run the pick-and-place:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config apriltag_pick_and_place.launch.py \
           use_sim_time:=true target_spawn:=false

Real
----

1. Open the Isaac Sim scene:
   ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/4c_apriltag_pick_and_place_real.usd``

2. Start WMX ROS2 for the manipulator on the robot (no ``use_sim_time``).

3. Launch the planner and AprilTag detector:

   .. tab-set::

      .. tab-item:: MoveIt2 OMPL + OpenCV AprilTag
         :sync: ompl

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_perception apriltag_detector.launch.py

      .. tab-item:: cuMotion + Isaac AprilTag
         :sync: cumotion

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_apriltag.launch.py

4. Run the pick-and-place (``target_spawn:=true`` spawns the target on the real
   setup):

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config apriltag_pick_and_place.launch.py \
           use_sim_time:=false target_spawn:=true
