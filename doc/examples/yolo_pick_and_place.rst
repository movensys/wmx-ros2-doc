YOLO Pick-and-Place
===================

Detect cubes and dice with YOLO and pick and place them. The detector moves to
a scan pose, visually servos over each detected object, picks it, and places it
in the per-class drop box. See :doc:`examples` for the shared manipulator
setup. All commands run through ``mros``.

.. tab-set::

   .. tab-item:: Simulation

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/LnLOdi9yG1I"
                  title="Yolo pick-and-place on simulation"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

         

      1. Open the Isaac Sim scene:
         ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/8a_yolo_pick_and_place_simulation.usd``

      2. Run the simulator bridge:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py use_sim_time:=true

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

      4. Launch the YOLO cube detector (the simulation scene contains cubes
         only):

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_perception yolo_cube_detector.launch.py use_sim_time:=true

      5. Execute the YOLO pick-and-place:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config yolo_pick_and_place.launch.py use_sim_time:=true

         (Pick/drop poses are loaded from ``config/<MANIPULATOR_MODEL>/yolo_trajectory.yaml``.)

         Debug the detections (optional):

         .. code-block:: bash

            ros2 run rqt_image_view rqt_image_view /yolo_cube_detector/debug_image

   .. tab-item:: HIL

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/LnLOdi9yG1I"
                  title="Yolo pick-and-place on hardware-in-the-loop (HIL)"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

         

      1. Open the Isaac Sim scene:
         ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/8b_yolo_pick_and_place_hil.usd``

      2. Start WMX R2 for the manipulator (real WMX runtime) with
         ``use_sim_time:=true`` (see
         ``~/workspaces/movensys_ws/src/wmx-r2/doc/launch_<MANIPULATOR_MODEL>_manipulator.md``).

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

         Add ``rsp:=false`` if using Gazebo or ``ros2_control`` -- both already
         publish ``/robot_description``.

      4. Launch the YOLO cube and dice detector:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_perception yolo_dice_and_cube_detector.launch.py use_sim_time:=true

      5. Execute the YOLO pick-and-place:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config yolo_pick_and_place.launch.py use_sim_time:=true

   .. tab-item:: Real

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/Bie7oQrH8rI"
                  title="Yolo pick-and-place on real-world scenario"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

      1. Open the Isaac Sim scene:
         ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/8c_yolo_pick_and_place_real.usd``

      2. Start WMX R2 for the manipulator on the robot (see
         ``~/workspaces/movensys_ws/src/wmx-r2/doc/launch_<MANIPULATOR_MODEL>_manipulator.md``).

      3. Launch the planner and service API:

         .. tab-set::

            .. tab-item:: MoveIt2 OMPL
               :sync: ompl

               .. code-block:: bash

                  mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py

            .. tab-item:: Isaac cuMotion
               :sync: cumotion

               .. code-block:: bash

                  mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion.launch.py

         Add ``rsp:=false`` if using Gazebo or ``ros2_control`` -- both already
         publish ``/robot_description``.

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
