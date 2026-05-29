Trajectory Planning
===================

Plan and execute joint and Cartesian trajectories with MoveIt2 (OMPL) or Isaac
cuMotion. See :doc:`examples` for the shared manipulator setup. All commands
run through ``mros``. For the programmatic ``/wmx/moveit2/*`` service API, see
:doc:`../integration/moveit2_integration`.

Simulation
----------

1. Open the scene:

   .. tab-set::

      .. tab-item:: Isaac Sim
         :sync: isaacsim

         Open
         ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/3a_trajectory_simulation.usd``

      .. tab-item:: Gazebo
         :sync: gazebo

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_description gazebo_trajectory_simulation.launch.py

2. Run the simulator bridge:

   .. tab-set::

      .. tab-item:: Isaac Sim
         :sync: isaacsim

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py \
                 simulator:=isaacsim use_sim_time:=true

      .. tab-item:: Gazebo
         :sync: gazebo

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py \
                 simulator:=gazebo use_sim_time:=true

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

4. (optional) Execute the trajectory or coverage test:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config trajectory_test.launch.py use_sim_time:=true
      mros ros2 launch movensys_manipulator_moveit_config coverage_pose.launch.py use_sim_time:=true

HIL
---

1. Open the scene:

   .. tab-set::

      .. tab-item:: Isaac Sim
         :sync: isaacsim

         Open
         ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/3b_trajectory_hil.usd``

      .. tab-item:: Gazebo
         :sync: gazebo

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_description gazebo_trajectory_hil.launch.py

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

4. (optional) Run ``trajectory_test.launch.py`` / ``coverage_pose.launch.py``
   with ``use_sim_time:=true``.

Real
----

1. (optional) Open the matching scene for visualization:

   .. tab-set::

      .. tab-item:: Isaac Sim
         :sync: isaacsim

         Open
         ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/3c_trajectory_real.usd``

      .. tab-item:: Gazebo
         :sync: gazebo

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_description gazebo_trajectory_real.launch.py

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

4. (optional) Run ``trajectory_test.launch.py`` / ``coverage_pose.launch.py``.
