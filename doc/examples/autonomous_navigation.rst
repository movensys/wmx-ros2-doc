Autonomous Navigation
=====================

Drive the base autonomously with the `Nav2 <https://docs.nav2.org/>`_ stack:
localize against the map saved in :doc:`slam_mapping`, set the initial pose, and
send goal poses that Nav2 plans and executes on the collision-aware
``/cmd_vel_safe`` topic. See :doc:`examples` for the shared navigation setup. All
commands run through ``nros``.

.. tab-set::

   .. tab-item:: Simulation

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/ZDK_gjjqmKA"
                  title="Autonomous navigation on simulation"
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

      3. Launch navigation:

         .. code-block:: bash

            nros ros2 launch movensys_navigation_nav2_config navigation.launch.py use_sim_time:=true

         Add ``rsp:=false`` if using Gazebo or ``ros2_control`` -- both already
         publish ``/robot_description``.

      4. Set the initial pose: in RViz, click **2D Pose Estimate** and click the map
         at the robot's current position and heading.

      5. Send a goal pose:

         .. code-block:: bash

            nros ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
              "'{pose: {header: {frame_id: map}, pose: {position: {x: 8.0, y: 0.0, z: 0.0}, \
              orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}}'"

   .. tab-item:: HIL

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/ZDK_gjjqmKA"
                  title="Autonomous navigation on HIL"
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

      3. Launch navigation:

         .. code-block:: bash

            nros ros2 launch movensys_navigation_nav2_config navigation.launch.py use_sim_time:=true

         Add ``rsp:=false`` if using Gazebo or ``ros2_control`` -- both already
         publish ``/robot_description``.


      4. Set the initial pose: in RViz, click **2D Pose Estimate** and click the map
         at the robot's current position and heading.

      5. Send a goal pose:

         .. code-block:: bash

            nros ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
              "'{pose: {header: {frame_id: map}, pose: {position: {x: 8.0, y: 0.0, z: 0.0}, \
              orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}}'"
