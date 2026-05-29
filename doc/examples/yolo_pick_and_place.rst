YOLO Pick-and-Place
===================

Detect cubes and dice with YOLO and pick and place them. The detector moves to
a scan pose, visually servos over each detected object, picks it, and places it
in the per-class drop box. See :doc:`examples` for the shared manipulator
setup. All commands run through ``mros``.

Simulation
----------

1. Open the Isaac Sim scene:
   ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/6a_robopoly_simulation.usd``

2. Run the simulator bridge:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py \
           simulator:=isaacsim use_sim_time:=true

3. Launch the planner and service API:

   .. tab-set::

      .. tab-item:: MoveIt2 OMPL
         :sync: ompl

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py use_sim_time:=true

      .. tab-item:: Isaac cuMotion
         :sync: cumotion

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion.launch.py use_sim_time:=true

4. Launch the YOLO cube and dice detector:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_perception yolo_dice_and_cube_detector.launch.py use_sim_time:=true

5. Execute the YOLO pick-and-place:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config yolo_pick_and_place.launch.py use_sim_time:=true

   (Pick/drop poses are loaded from ``config/<MANIPULATOR_MODEL>/yolo_trajectory.yaml``.)

   Debug the detections (optional):

   .. code-block:: bash

      ros2 run rqt_image_view rqt_image_view /yolo_dice_detector/debug_image
      ros2 run rqt_image_view rqt_image_view /yolo_cube_detector/debug_image

HIL
---

1. Open the Isaac Sim scene:
   ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/6b_robopoly_hil.usd``

2. Start WMX ROS2 for the manipulator (real WMX runtime) with
   ``use_sim_time:=true``.

3. Launch the planner and service API with ``use_sim_time:=true``:

   .. tab-set::

      .. tab-item:: MoveIt2 OMPL
         :sync: ompl

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py use_sim_time:=true

      .. tab-item:: Isaac cuMotion
         :sync: cumotion

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion.launch.py use_sim_time:=true

4. Launch the YOLO detector:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_perception yolo_dice_and_cube_detector.launch.py use_sim_time:=true

5. Execute the YOLO pick-and-place:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config yolo_pick_and_place.launch.py use_sim_time:=true

Real
----

1. Open the Isaac Sim scene:
   ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/6c_robopoly_real.usd``

2. Start WMX ROS2 for the manipulator on the robot (no ``use_sim_time``).

3. Launch the planner and service API (no ``use_sim_time``):

   .. tab-set::

      .. tab-item:: MoveIt2 OMPL
         :sync: ompl

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py

      .. tab-item:: Isaac cuMotion
         :sync: cumotion

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion.launch.py

4. Launch the YOLO cube and dice detector:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_perception yolo_dice_and_cube_detector.launch.py

   Debug the detections (optional):

   .. code-block:: bash

      ros2 run rqt_image_view rqt_image_view /yolo_dice_detector/debug_image
      ros2 run rqt_image_view rqt_image_view /yolo_cube_detector/debug_image

5. (optional) Execute the YOLO pick-and-place:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config yolo_pick_and_place.launch.py

.. note::

   The YOLO pick-and-place is the perception layer used by the
   :doc:`robopoly_game`, which adds voice and VLM/LLM control on top.
