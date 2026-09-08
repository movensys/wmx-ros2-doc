AprilTag + Obstacle Avoidance
=============================

Combines AprilTag-driven pick-and-place with Nvblox obstacle avoidance: Isaac
cuMotion plans collision-free motion against a live Nvblox reconstruction while
Isaac ROS AprilTag locates the target. See :doc:`examples` for the shared
manipulator setup. All commands run through ``mros``.

.. tab-set::

   .. tab-item:: Simulation

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/vRgbOcu9tlA"
                  title="AprilTag based obstacle avoidance on simulation"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

      1. Open the Isaac Sim scene:
         ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/6a_apriltag_obstacle_avoidance_simulation.usd``

      2. Run the simulator bridge:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py use_sim_time:=true

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

   .. tab-item:: HIL

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/vRgbOcu9tlA"
                  title="AprilTag based obstacle avoidance on hardware-in-the-loop (HIL)"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

      1. Open the Isaac Sim scene:
         ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/6b_apriltag_obstacle_avoidance_hil.usd``

      2. Start WMX R2 for the manipulator (real WMX runtime) with
         ``use_sim_time:=true`` (see
         ``~/workspaces/movensys_ws/src/wmx-r2/doc/launch_<MANIPULATOR_MODEL>_manipulator.md``).

      3. Launch cuMotion + Nvblox:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_nvblox.launch.py use_sim_time:=true

         Add ``rsp:=false`` if using Gazebo or ``ros2_control`` -- both already
         publish ``/robot_description``.

      4. Launch Isaac AprilTag:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_apriltag.launch.py use_sim_time:=true

      5. Run AprilTag pick-and-place with obstacle avoidance:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config apriltag_pick_and_place.launch.py \
                 use_sim_time:=true target_spawn:=false

   .. tab-item:: Real

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/aOroNhUoc9s"
                  title="AprilTag based obstacle avoidance on real-world scenario"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

      1. Open the Isaac Sim scene:
         ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/6c_apriltag_obstacle_avoidance_real.usd``

      2. Start WMX R2 for the manipulator on the robot (see
         ``~/workspaces/movensys_ws/src/wmx-r2/doc/launch_<MANIPULATOR_MODEL>_manipulator.md``).

      3. Launch cuMotion + Nvblox:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_nvblox.launch.py

         Add ``rsp:=false`` if using Gazebo or ``ros2_control`` -- both already
         publish ``/robot_description``.

      4. Launch Isaac AprilTag:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_apriltag.launch.py

      5. Run AprilTag pick-and-place with obstacle avoidance:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config apriltag_pick_and_place.launch.py \
                 use_sim_time:=false target_spawn:=true
