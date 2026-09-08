Commissioning and First Motion
==============================

.. warning::

   Do not start this procedure until :doc:`robot_parameters` is complete and
   the same configuration has run cleanly in Simulation and HIL. This is
   stage 4 of the :ref:`simulation-first-workflow`. The purpose of this
   procedure is to *discover* wrong parameters with the robot moving slowly
   and by small amounts, which is the only cheap way to find them.

   Before the first command, confirm that the separate safety measures
   described in :doc:`safety` are installed and tested — in particular a
   hardwired emergency stop that removes drive power independently of this
   software.

Preconditions
-------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Check
     - Requirement
   * - Parameter review
     - :doc:`robot_parameters` completed; the joint↔axis table written down
   * - Simulation
     - The same URDF and MoveIt configuration planned and executed correctly
   * - HIL
     - The real WMX runtime loaded your parameter file and executed a
       trajectory against the simulated bus with no errors
   * - Workspace
     - The robot is clear of people, fixtures, cabling, and the ground plane
       through its full expected travel — not just its current pose
   * - Emergency stop
     - A hardwired E-stop that removes drive power is installed, reachable
       from the operating position, and has been function-tested this session
   * - Mechanical
     - Payload and tooling removed or fully secured; brakes, if fitted,
       verified to hold
   * - Recovery
     - You know how to clear an alarm and how to restore power after an E-stop

Stage 4A — Bring the axes up without commanding motion
--------------------------------------------------------

Start only the general nodes. This path uses no planner, no MoveIt, and no
Servo, so nothing can generate a trajectory while you are still checking
feedback.

.. code-block:: bash

   sudo --preserve-env=PATH \
     --preserve-env=AMENT_PREFIX_PATH \
     --preserve-env=COLCON_PREFIX_PATH \
     --preserve-env=PYTHONPATH \
     --preserve-env=LD_LIBRARY_PATH \
     --preserve-env=ROS_DISTRO \
     --preserve-env=ROS_VERSION \
     --preserve-env=ROS_PYTHON_VERSION \
     --preserve-env=ROS_DOMAIN_ID \
     --preserve-env=RMW_IMPLEMENTATION \
     bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && source $HOME/workspaces/movensys_ws/install/setup.bash && \
     ros2 launch wmx_r2_package wmx_r2_general_nodes.launch.py"

Wait for the lifecycle manager to bring the nodes up — the ``/wmx/axes/*``
services do not exist until ``wmx_core_motion_node`` is ``active``:

.. code-block:: bash

   ros2 service call /wmx/lifecycle/get_node_states \
        wmx_r2_message/srv/GetNodeStates "{}"

Confirm the engine and the bus, then read back the parameters the engine
actually holds:

.. code-block:: bash

   ros2 service call /wmx/engine/get_engine_status std_srvs/srv/Trigger "{}"   # expect "Communicating"
   ros2 service call /wmx/ecat/get_master_info \
        wmx_r2_message/srv/EcatGetMasterInfo "{master_id: 0}"     # expect every drive present
   ros2 service call /wmx/engine/get_axis_param wmx_r2_message/srv/GetAxisParam \
        "{axis: [0,1,2,3,4,5]}"                                      # gear ratio, polarity, mode

**Checkpoint.** The gear ratio, polarity, and command mode in the response
must match the table you built in :doc:`robot_parameters`. Stop here if they
do not.

Now watch the feedback with the servos still off and move each joint **by
hand** where the mechanics allow it:

.. code-block:: bash

   ros2 topic echo /wmx/axes/status

.. list-table:: What to confirm before enabling a servo
   :header-rows: 1
   :widths: 34 66

   * - Check
     - Expected
   * - ``amp_alarm``
     - all ``false``
   * - ``actual_pos``
     - plausible values, and stable when nothing is moving
   * - Joint numbering
     - moving physical joint *N* by hand changes ``actual_pos[N-1]`` and no
       other entry
   * - Direction
     - moving a joint in the URDF's positive direction increases
       ``actual_pos`` for that axis
   * - Magnitude
     - a hand-moved 90° rotation changes ``actual_pos`` by ≈ 1.571; a value
       that is off by a large factor means the gear ratio is wrong

.. note::

   This hand-check catches swapped axes, inverted polarity, and wrong gear
   ratios **before any motor is energized**. It is the highest-value step in
   the whole procedure. On a robot whose joints cannot be back-driven, defer
   these three checks to stage 4B and use the smallest steps in the table.

Stage 4B — One axis, low speed, small step
--------------------------------------------

Enable **one** axis only. Leave every other axis off.

.. code-block:: bash

   ros2 service call /wmx/axes/clear_amp_alarm wmx_r2_message/srv/SetAxes \
        "{axis: [0], data: [0]}"
   ros2 service call /wmx/axes/set_servo_on wmx_r2_message/srv/SetAxes \
        "{axis: [0], data: [1]}"

Command a small relative move. The units are radians, and the velocity and
acceleration are rad/s and rad/s² (this holds only because
``AxisGearRatioDenominator`` is 2π — see :doc:`robot_parameters`):

.. code-block:: bash

   # +0.05 rad (≈2.9°) at 0.05 rad/s with gentle ramps
   ros2 service call /wmx/axes/start_mov wmx_r2_message/srv/StartAxesPose \
     "{axis: [0], target: [0.05], velocity: [0.05], acc: [0.1], dec: [0.1]}"

.. warning::

   The examples in :doc:`../api_reference/ros2_services` use values such as
   ``velocity: [10]`` to illustrate the request format. Those are **not**
   commissioning values. For a first move use velocity ≤ 0.05 rad/s and
   acceleration ≤ 0.1 rad/s², and increase only after each check below
   passes.

Work through this sequence for the axis, repeating each step in both
directions:

.. list-table::
   :header-rows: 1
   :widths: 6 26 68

   * - #
     - Check
     - How
   * - 1
     - **Joint numbering**
     - Command ``axis: [0]``. Confirm that the joint you mapped to axis 0
       moves and that nothing else does. Repeat for every axis before
       continuing.
   * - 2
     - **Direction**
     - Command ``target: [+0.05]``. The joint must rotate in the direction
       the URDF calls positive, and RViz must move the same way as the
       physical robot. If it is reversed, correct ``AxisPolarity`` — do not
       compensate for it elsewhere.
   * - 3
     - **Travel distance**
     - Command ``target: [+0.5]`` (≈28.6°) and measure the physical rotation
       with an inclinometer or a marked reference. A discrepancy is a gear
       ratio or encoder-resolution error. Do not scale it away in the URDF.
   * - 4
     - **Home position**
     - Move the joint to a known mechanical reference (a machined face, a
       scribed mark, a mechanical stop approached slowly). Compare
       ``actual_pos`` against the value the URDF zero implies. A constant
       offset on all moves is an ``AbsoluteEncoderHomeOffset`` error.
   * - 5
     - **Feedback agreement**
     - With the axis stationary, ``pos_cmd`` and ``actual_pos`` must agree to
       within the in-position window. A growing gap during motion is a
       following error — stop and investigate before increasing speed.
   * - 6
     - **Range of travel**
     - Approach each end of the intended travel in small steps at low speed,
       confirming the mechanical range matches the URDF limits. Remember that
       WMX soft limits are **disabled** in the shipped parameter files.

Disable the axis before moving to the next one:

.. code-block:: bash

   ros2 service call /wmx/axes/set_servo_on wmx_r2_message/srv/SetAxes \
        "{axis: [0], data: [0]}"

**Checkpoint.** Do not proceed to multi-axis motion until every axis has
passed checks 1–6 individually.

Stage 5 — Multi-axis motion
-----------------------------

Only after every axis has passed individually:

1. Enable all axes and command each one in turn from a single node, still at
   commissioning speeds, confirming no cross-talk.
2. Bring up the planner (``moveit.launch.py``) and plan — but do not execute —
   a short motion. Confirm in RViz that the planned path matches the physical
   robot's current pose.
3. Execute one short, slow, coordinated motion well inside the workspace, with
   a hand on the E-stop.
4. Increase speed toward the configured limits in steps, re-checking following
   error at each step.

Stage 6 — Trajectory execution
--------------------------------

Run the trajectory examples in :doc:`../examples/trajectory_planning`, keeping
MoveIt's velocity and acceleration scaling low for the first runs and raising
it once tracking is confirmed.

.. _keyboard-jogging-behavior:

Keyboard jogging — speeds, steps, and stopping behavior
---------------------------------------------------------

``keyboard_teleop`` is a convenience tool for driving MoveIt Servo. It is
**not** a commissioning tool: it needs the whole planner stack up, it moves the
end effector rather than one axis, and its speeds are set in ``servo.yaml``
rather than per command. Use the ``/wmx/axes/start_mov`` procedure
above for stages 4A and 4B, and keyboard jogging afterwards.

The key mappings are in :ref:`keyboard-jogging`. The quantities that matter
for safety are below, as configured for the CR3A in
``movensys_manipulator_moveit_config/config/dobot_cr3a/servo.yaml``.

.. list-table:: Jog speeds and steps
   :header-rows: 1
   :widths: 24 20 56

   * - Mode
     - Configured value
     - Meaning
   * - JOINT (``1``…``6``)
     - ``scale.joint`` = 0.5 rad/s
     - One keypress requests full-scale jog velocity for that joint until the
       command times out.
   * - TWIST — linear
     - ``scale.linear`` = 0.4 m/s
     - Maximum commanded end-effector linear speed.
   * - TWIST — angular
     - ``scale.rotational`` = 0.8 rad/s
     - Maximum commanded end-effector angular speed.
   * - POSE
     - 0.01 m per keypress
     - Each keypress shifts an **absolute** target by 10 mm. The target is
       then streamed continuously at ~50 Hz, so the arm drives to it and holds
       it.
   * - Command rate
     - ``publish_period`` = 0.025 s
     - Servo emits a command roughly every 25 ms (~40 Hz).

.. list-table:: Stopping behavior
   :header-rows: 1
   :widths: 30 70

   * - Mechanism
     - Behavior
   * - Command timeout
     - ``incoming_command_timeout`` = 0.1 s. In JOINT and TWIST mode a
       keypress sends a single command, so motion stops ~0.1 s after the last
       keypress. Servo then publishes
       ``num_outgoing_halt_msgs_to_publish`` = 4 halt messages.
   * - Per-keypress travel
     - JOINT mode: roughly 0.5 rad/s for ~0.1 s, i.e. on the order of
       0.05 rad (≈3°) per keypress, reduced by the smoothing filter. **Measure
       it on your robot** rather than relying on this estimate.
   * - POSE mode
     - Does **not** time out. ``keyboard_teleop`` re-publishes the target
       every 20 ms, so the arm keeps driving to the accumulated target and
       holds position there until you move the target or stop the node.
   * - Joint-limit margin
     - ``joint_limit_margins`` = 0.1 rad. Servo slows as a joint approaches
       its URDF limit.
   * - Singularity
     - Servo scales velocity down above condition number 17 and stops above
       30.
   * - Collision
     - ``check_collisions`` is enabled at 10 Hz against the monitored planning
       scene. It protects against modelled geometry only.
   * - ``q``
     - Restores the terminal and shuts the ``keyboard_teleop`` node down.
   * - ``Ctrl+C``
     - Same handler as ``q``.

.. danger:: **``q`` and ``Ctrl+C`` are not emergency stops.**

   Both do exactly one thing: they terminate the ``keyboard_teleop`` process.
   Motion then stops only as a side effect — Servo stops receiving commands
   and halts after its 0.1 s timeout.

   Neither one:

   - removes power from the motors — the servos stay enabled and holding,
   - engages the mechanical brakes,
   - triggers STO or any drive-level safe stop,
   - stops the WMX engine or EtherCAT communication,
   - has any redundancy, monitoring, or guaranteed stopping time,
   - affects anything else that is commanding the robot. A ``move_group``
     trajectory already in flight continues to completion.

   They depend on the operating system scheduling a process, on ROS 2
   middleware delivery, and on the correct behavior of the software you are in
   the middle of commissioning. An emergency stop must be a hardwired circuit
   that removes drive power independently of all of it. See :doc:`safety`.

To stop motion deliberately from ROS 2, disable the servos — which is a
controlled stop, still not an emergency stop:

.. code-block:: bash

   ros2 service call /wmx/axes/set_servo_on wmx_r2_message/srv/SetAxes \
        "{axis: [0,1,2,3,4,5], data: [0,0,0,0,0,0]}"

.. warning:: **Known limitation — ``keyboard_teleop`` forces simulated time.**

   ``keyboard_teleop`` sets ``use_sim_time`` to ``true`` unconditionally in
   its node options; there is no launch argument to turn it off. On a physical
   robot run without a ``/clock`` publisher, the node's clock does not advance,
   so the timestamps on its jog messages are not real time. Confirm the arm
   responds as expected in HIL before relying on keyboard jogging on hardware,
   and prefer the ``/wmx/axes/start_mov`` procedure above for
   commissioning.

Record what you verified
--------------------------

Commissioning results are per robot, not per model. Two units of the same
model can differ in encoder zero, motor orientation, and mechanical range.
Record, for each axis: the ROS 2 joint name, the WMX axis index, the EtherCAT
position, the gear ratio numerator, the polarity, the measured travel for a
known command, the home offset, and the measured mechanical range. Keep it
with the parameter file — it is what makes the next commissioning, or the next
service visit, a check rather than a rediscovery.
