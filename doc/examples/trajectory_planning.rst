Trajectory Planning
===================

Plan and execute joint and Cartesian trajectories with MoveIt2 (OMPL) or Isaac
cuMotion. See :doc:`examples` for the shared manipulator setup. All commands
run through ``mros``. For the programmatic ``/wmx/moveit2/*`` service API, see
:doc:`../integration/moveit2_integration`.

.. tab-set::

   .. tab-item:: Simulation
   
      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/BcstJiR7Vik"
                  title="Basic movements on simulation"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

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

      2. Run the simulator bridge. The same command serves both simulators:

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

         Add ``rsp:=false`` if using Gazebo or ``ros2_control`` -- both already
         publish ``/robot_description``.

      4. (optional) Jog the arm from the keyboard (see :ref:`keyboard-jogging`):

         .. code-block:: bash

            mros ros2 run movensys_manipulator_moveit_config keyboard_teleop

      5. (optional) Execute the trajectory or coverage test:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config trajectory_test.launch.py use_sim_time:=true
            mros ros2 launch movensys_manipulator_moveit_config coverage_pose.launch.py use_sim_time:=true

   .. tab-item:: HIL

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/BcstJiR7Vik"
                  title="Basic movements on hardware-in-the-loop (HIL)"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

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

      4. (optional) Jog the arm from the keyboard (see :ref:`keyboard-jogging`):

         .. code-block:: bash

            mros ros2 run movensys_manipulator_moveit_config keyboard_teleop

      5. (optional) Execute the trajectory or coverage test:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config trajectory_test.launch.py use_sim_time:=true
            mros ros2 launch movensys_manipulator_moveit_config coverage_pose.launch.py use_sim_time:=true

   .. tab-item:: Real

      .. raw:: html

         <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
         <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
                  src="https://www.youtube-nocookie.com/embed/ShQzq_v2qWE"
                  title="Basic movements on real-world scenario"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowfullscreen></iframe>
         </div>

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

      4. (optional) Jog the arm from the keyboard (see :ref:`keyboard-jogging`):

         .. code-block:: bash

            mros ros2 run movensys_manipulator_moveit_config keyboard_teleop

      5. (optional) Execute the trajectory or coverage test:

         .. code-block:: bash

            mros ros2 launch movensys_manipulator_moveit_config trajectory_test.launch.py
            mros ros2 launch movensys_manipulator_moveit_config coverage_pose.launch.py

.. _keyboard-jogging:

Keyboard Jogging
----------------

``keyboard_teleop`` drives the ``servo_node`` started by ``moveit.launch.py``,
so it works in any of the three modes once the planner is up. Pick a mode first
(``j`` / ``t`` / ``p``), then jog.

.. danger::

   ``q`` and ``Ctrl+C`` are **not** emergency stops. They terminate the
   ``keyboard_teleop`` process; motion stops only as a side effect, after
   Servo's 0.1 s command timeout. Neither removes motor power, engages brakes,
   triggers STO, or stops a ``move_group`` trajectory that is already
   executing.

.. note::

   This table is the key mapping only. For the configured jog speeds, the
   per-keypress step size, the command timeout, and the exact stopping
   behavior of each mode, see
   :ref:`keyboard-jogging-behavior`. On a physical robot, do not use keyboard
   jogging as the first motion. Follow :doc:`../commissioning/first_motion`
   first.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Key
     - Action
   * - ``j``
     - **JOINT** mode -- keys ``1``…``6`` jog joint 1…6
   * - ``t``
     - **TWIST** mode -- Cartesian end-effector jog
   * - ``p``
     - **POSE** mode -- nudge an absolute end-effector target pose
   * - ``↑`` / ``↓``
     - X (+ / −) -- twist jog, or pose-target nudge
   * - ``←`` / ``→``
     - Y (− / +) -- twist jog, or pose-target nudge
   * - ``.`` / ``;``
     - Z (− / +) -- twist jog, or pose-target nudge
   * - ``1`` … ``6``
     - Joint jog for joint 1 … 6 (JOINT mode)
   * - ``w`` / ``e``
     - Frame for TWIST jog **and** POSE nudge = base (``world_manipulator``) /
       eef (``Link6``)
   * - ``r``
     - Reverse jog direction (twist / joint)
   * - ``q``
     - Quit
