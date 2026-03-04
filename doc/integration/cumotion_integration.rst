Isaac cuMotion Accelerated Planning
=====================================

Overview
--------

NVIDIA Isaac cuMotion provides GPU-accelerated trajectory planning as an
alternative to the default MoveIt2 OMPL planners. It leverages CUDA parallel
processing to achieve significantly faster planning times, especially for
collision-constrained environments. cuMotion integrates as a drop-in MoveIt2
planning pipeline replacement -- no changes to the WMX ROS2 nodes are required.

Prerequisites
-------------

- NVIDIA GPU with CUDA support (RTX 5070 or better recommended)
- Ubuntu 22.04 with NVIDIA drivers installed
- ROS2 Humble
- Isaac ROS packages installed in a Docker container (see
  ``movensys_isaac_manipulator/doc/2_docker.md`` for setup)
- ``movensys_manipulator_isaac_config`` workspace built inside the container
- WMX ROS2 application built on the IPC (see :doc:`../getting_started/index`)

Integration
-----------

cuMotion sends planned trajectories to the same
``/movensys_manipulator_arm_controller/follow_joint_trajectory`` action server
that MoveIt2 uses. The ``follow_joint_trajectory_server`` node executes them
identically -- no WMX node changes are needed.

The Orin platform config (``orin_manipulator_config_cr3a.yaml``) enables the
``isaacsim_joint_topic`` parameter so joint states are forwarded to Isaac Sim.
See :doc:`../packages/wmx_ros2_package` for configuration details and
:doc:`../api_reference/ros2_actions` for action server details.

.. list-table:: Key Differences from Stage 1 (MoveIt2 OMPL)
   :header-rows: 1
   :widths: 30 70

   * - Aspect
     - cuMotion (Stage 2)
   * - Planning pipeline
     - cuMotion replaces OMPL as the MoveIt2 planner backend
   * - Robot description
     - XRDF (Extended Robot Description Format) loaded for GPU optimization
   * - Execution environment
     - Planner runs inside the Isaac ROS Docker container with GPU access
   * - Hardware interface
     - Same ``FollowJointTrajectory`` action -- no WMX changes needed
   * - Planning speed
     - Typically faster due to GPU parallelism

Stage 2a -- Simulation
-----------------------

Run cuMotion with Isaac Sim on the same machine (no physical robot).

**Step 1: Open Isaac Sim**

Open the simulation scene:

.. code-block:: text

   ~/robotics_isaac_sim/isaac_manipulator/simulation_1_to_3.usd

**Step 2: Launch the Simulation Bridge**

.. code-block:: bash

   ros2 run movensys_manipulator_isaac_config simulation_action \
     --ros-args -p use_sim_time:=true

**Step 3: Launch cuMotion Planner (Docker)**

.. code-block:: bash

   docker exec -u admin -it movensys_isaac_manipulator_container \
     bash -lc 'source /opt/ros/humble/setup.bash && \
               source /home/admin/ws/install/setup.bash && \
               ros2 launch movensys_manipulator_isaac_config \
                 isaac_cumotion.launch.py use_sim_time:=true'

**Step 4: Execute Trajectory Test**

.. code-block:: bash

   ros2 launch movensys_manipulator_isaac_config \
     stage1and2_trajectory.launch.py use_sim_time:=true

Stage 2b -- Hardware-in-the-Loop (HiL)
----------------------------------------

Run cuMotion planning in Isaac Sim while executing on the physical robot (IPC).

**Step 1: Open Isaac Sim [Desktop]**

Open the HiL scene:

.. code-block:: text

   ~/robotics_isaac_sim/isaac_manipulator/hil_1_to_3.usd

**Step 2: Launch WMX ROS2 Manipulator [IPC]**

.. code-block:: bash

   sudo --preserve-env=PATH,AMENT_PREFIX_PATH,COLCON_PREFIX_PATH,PYTHONPATH,\
   LD_LIBRARY_PATH,ROS_DISTRO,ROS_VERSION,ROS_PYTHON_VERSION,ROS_DOMAIN_ID,\
   RMW_IMPLEMENTATION \
     bash -c "source /opt/ros/humble/setup.bash && \
              source ~/wmx_ros2_ws/install/setup.bash && \
              ros2 launch wmx_ros2_package \
                wmx_ros2_orin_manipulator_cr3a.launch.py"

**Step 3: Launch cuMotion [IPC]**

.. code-block:: bash

   docker exec -u admin -it movensys_isaac_manipulator_container \
     bash -lc 'source /opt/ros/humble/setup.bash && \
               source /home/admin/ws/install/setup.bash && \
               ros2 launch movensys_manipulator_isaac_config \
                 isaac_cumotion.launch.py'

**Step 4: Launch Trajectory [IPC]**

.. code-block:: bash

   ros2 launch movensys_manipulator_isaac_config stage1and2_trajectory.launch.py

Stage 2c -- Real Robot (No Simulation)
----------------------------------------

Run cuMotion planning and execute on the physical robot with no Isaac Sim
digital twin. Uses the same launch sequence as HiL but with a different USD
scene.

**Step 1: Open Isaac Sim [Desktop]**

Open the real-robot scene:

.. code-block:: text

   ~/robotics_isaac_sim/isaac_manipulator/demo_full.usd

**Step 2: Launch WMX ROS2 Manipulator [IPC]**

Same command as Stage 2b Step 2.

**Step 3: Launch cuMotion [IPC]**

Same command as Stage 2b Step 3.

**Step 4: Launch Trajectory [IPC]**

.. code-block:: bash

   ros2 launch movensys_manipulator_isaac_config stage1and2_trajectory.launch.py

See Also
--------

- :doc:`../examples/isaac_manipulator` -- Full stage-by-stage Isaac manipulator demo
- :doc:`../api_reference/ros2_actions` -- FollowJointTrajectory action details
- :doc:`../packages/wmx_ros2_package` -- Orin configuration file parameters
- :doc:`moveit2_integration` -- Stage 1 MoveIt2 OMPL planning
