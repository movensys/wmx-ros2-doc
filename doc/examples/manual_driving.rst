Manual Driving
==============

Drive the differential-drive base manually with keyboard teleop, publishing
velocity commands through the collision-aware ``/cmd_vel_safe`` topic. This is
the simplest navigation scenario and a good way to confirm the base, odometry
(EKF), and robot state publisher (RSP) are wired up before mapping or
autonomous navigation. See :doc:`examples` for the shared navigation setup. All
commands run through ``nros``.


.. tab-set::

   .. tab-item:: Simulation
      
      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/OPnAxtBSfoU"
                  title="Manual driving on simulation"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

      1. Open the scene:

         .. tab-set::

            .. tab-item:: Isaac Sim
               :sync: isaacsim

               Open
               ``~/workspaces/movensys-simulation/<NAVIGATION_MODEL>/navigation_simulation.usd``

            .. tab-item:: Gazebo
               :sync: gazebo

               .. code-block:: bash

                  nros ros2 launch movensys_navigation_description gazebo_navigation_simulation.launch.py

      2. Run the simulator bridge:

         .. code-block:: bash

            nros ros2 launch movensys_navigation_nav2_config sim_bridge.launch.py use_sim_time:=true

      3. Run the EKF + robot state publisher:

         .. code-block:: bash

            nros ros2 launch movensys_navigation_nav2_config base.launch.py use_sim_time:=true

         Add ``rsp:=false`` if using Gazebo or ``ros2_control`` -- both already
         publish ``/robot_description``.

      4. Drive with the teleop keyboard:

         .. code-block:: bash

            nros ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args \
                 -p turn:=0.5 \
                 -p stamped:=true \
                 -p frame_id:=base_link \
                 -p use_sim_time:=true \
                 -r cmd_vel:=/cmd_vel_safe

         Keep this terminal focused to send keystrokes to the base.

   .. tab-item:: HIL

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/OPnAxtBSfoU"
                  title="Manual driving on HIL"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

      1. Open the scene:

         .. tab-set::

            .. tab-item:: Isaac Sim
               :sync: isaacsim

               Open
               ``~/workspaces/movensys-simulation/<NAVIGATION_MODEL>/navigation_hil.usd``

            .. tab-item:: Gazebo
               :sync: gazebo

               Not applicable for HIL.

      2. Start WMX R2 for the navigation base (real WMX runtime) with
         ``use_sim_time:=true`` (see
         ``~/workspaces/movensys_ws/src/wmx-r2/doc/launch_<NAVIGATION_MODEL>_navigation.md``).

      3. Run the EKF + robot state publisher:

         .. code-block:: bash

            nros ros2 launch movensys_navigation_nav2_config base.launch.py use_sim_time:=true

         Add ``rsp:=false`` if using Gazebo or ``ros2_control`` -- both already
         publish ``/robot_description``.

      4. Drive with the teleop keyboard:

         .. code-block:: bash

            nros ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args \
                 -p turn:=0.5 \
                 -p stamped:=true \
                 -p frame_id:=base_link \
                 -p use_sim_time:=true \
                 -r cmd_vel:=/cmd_vel_safe
