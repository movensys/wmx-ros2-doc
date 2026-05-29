Isaac cuMotion Accelerated Planning
=====================================

Overview
--------

NVIDIA Isaac cuMotion provides GPU-accelerated trajectory planning as an
alternative to the default MoveIt2 OMPL planners. It plugs into MoveIt2 as the
planning pipeline, so the rest of the stack is unchanged: planned trajectories
still flow through the ``trajectory_api`` services and execute on the WMX
``joint_trajectory_controller``. cuMotion is provided by the
``movensys_manipulator_isaac_ros_config`` package in the
`movensys-manipulator <https://github.com/movensys/movensys-manipulator>`_
repository.

Prerequisites
-------------

- An NVIDIA GPU with CUDA (NVIDIA desktop GPU or Jetson)
- Isaac ROS prerequisites (see the
  `Isaac ROS getting-started guide <https://nvidia-isaac-ros.github.io/getting_started/index.html>`_)
- The ``movensys-manipulator`` container built with an Isaac ROS image, i.e.
  ``MOVENSYS_ROS_VERSION=isaac-ros_4.1`` or ``isaac-ros_3.2``
- For Isaac Sim scenes, the
  `movensys-simulation <https://github.com/movensys/movensys-simulation>`_ repo

See :doc:`moveit2_integration` for the shared MoveIt2 setup and the ``mros``
container workflow.

Running cuMotion
----------------

cuMotion runs alongside the MoveIt2 stack. Start ``move_group`` and the
trajectory services as usual, then launch the cuMotion planner. Commands run
through the ``mros`` container helper.

**Real robot:**

.. code-block:: bash

   # MoveIt2 (move_group + trajectory_api services)
   mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py

   # Isaac cuMotion planner
   mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion.launch.py

   # Run a trajectory
   mros ros2 launch movensys_manipulator_moveit_config trajectory_test.launch.py

**Simulation / hardware-in-the-loop:** start the simulator bridge first and add
``use_sim_time:=true`` to each command:

.. code-block:: bash

   mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py \
        simulator:=isaacsim use_sim_time:=true
   mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py \
        use_sim_time:=true
   mros ros2 launch movensys_manipulator_isaac_ros_config isaac_cumotion.launch.py \
        use_sim_time:=true

Obstacle Avoidance (Nvblox)
---------------------------

For collision-aware planning against a live depth reconstruction, use the
combined cuMotion + Nvblox launch together with the obstacle-avoidance demo:

.. code-block:: bash

   mros ros2 launch movensys_manipulator_isaac_ros_config \
        isaac_cumotion_nvblox.launch.py use_sim_time:=true
   mros ros2 launch movensys_manipulator_moveit_config \
        obstacle_avoidance.launch.py use_sim_time:=true

Additional Isaac ROS launch files include ``isaac_apriltag.launch.py``,
``isaac_nvblox.launch.py``, and ``isaac_cumotion_apriltag.launch.py`` for the
AprilTag and combined perception scenarios.

cuMotion vs. MoveIt2 OMPL
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Aspect
     - cuMotion
   * - Planning pipeline
     - GPU-accelerated planner that replaces OMPL inside MoveIt2
   * - Execution
     - Same ``trajectory_api`` services and WMX ``joint_trajectory_controller``
   * - Best for
     - Collision-constrained planning, obstacle avoidance with Nvblox
   * - Hardware
     - Requires an NVIDIA GPU and an Isaac ROS image

See Also
--------

- :doc:`moveit2_integration` -- MoveIt2 setup and the ``/wmx/moveit2/*`` API
- :doc:`../examples/examples` -- end-to-end manipulator examples
- The `movensys-manipulator <https://github.com/movensys/movensys-manipulator>`_
  repository for the AprilTag, Nvblox, and YOLO walkthroughs
