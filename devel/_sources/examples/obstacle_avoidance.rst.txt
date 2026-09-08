Nvblox Obstacle Avoidance
=========================

Collision-aware planning with Isaac cuMotion against a live Nvblox depth
reconstruction. See :doc:`examples` for the shared manipulator setup. All
commands run through ``mros``.

.. tab-set::

   .. tab-item:: Simulation

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/7bK1Ivz4x1g"
                  title="Collision-aware planning on simulation"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>
         

      1. Open the Isaac Sim scene:
         ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/5a_obstacle_avoidance_simulation.usd``

      2. Run the simulator bridge:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py use_sim_time:=true

      3. Launch cuMotion + Nvblox:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_nvblox.launch.py use_sim_time:=true

      4. Run obstacle avoidance:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config obstacle_avoidance.launch.py use_sim_time:=true

      5. (optional) Tune the Nvblox camera transform:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_perception camera_transform_tuning.launch.py use_sim_time:=true \
                 parent_frame:=world_manipulator child_frame:=camera_nvblox_color_optical_frame

   .. tab-item:: HIL

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/7bK1Ivz4x1g"
                  title="Collision-aware planning on hardware-in-the-loop (HIL)"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

      1. Open the Isaac Sim scene:
         ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/5b_obstacle_avoidance_hil.usd``

      2. Start WMX R2 for the manipulator (real WMX runtime) with
         ``use_sim_time:=true`` (see
         ``~/workspaces/movensys_ws/src/wmx-r2/doc/launch_<MANIPULATOR_MODEL>_manipulator.md``).

      3. Launch cuMotion + Nvblox:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_nvblox.launch.py use_sim_time:=true

         Add ``rsp:=false`` if using Gazebo or ``ros2_control`` -- both already
         publish ``/robot_description``.

      4. Run obstacle avoidance:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config obstacle_avoidance.launch.py use_sim_time:=true

      5. (optional) Tune the Nvblox camera transform (same command as Simulation
         step 5).

   .. tab-item:: Real

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/1rNdSziHcbc"
                  title="Collision-aware planning on real-world scenario"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

         

      1. Open the Isaac Sim scene:
         ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/5c_obstacle_avoidance_real.usd``

      2. Start WMX R2 for the manipulator on the robot (see
         ``~/workspaces/movensys_ws/src/wmx-r2/doc/launch_<MANIPULATOR_MODEL>_manipulator.md``).

      3. Launch cuMotion + Nvblox:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion_nvblox.launch.py

         Add ``rsp:=false`` if using Gazebo or ``ros2_control`` -- both already
         publish ``/robot_description``.

      4. Run obstacle avoidance:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config obstacle_avoidance.launch.py

      5. (optional) Tune the Nvblox camera transform (note the real-hardware frame):

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_perception camera_transform_tuning.launch.py \
                 parent_frame:=world_manipulator child_frame:=camera_nvblox_link
