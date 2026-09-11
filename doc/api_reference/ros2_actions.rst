ROS2 Actions
=============

The WMX R2 application exposes one action server for trajectory execution,
compatible with MoveIt2 and any ``FollowJointTrajectory`` action client. No
custom ``.action`` files are defined -- the system uses the standard
``control_msgs`` action type.

.. list-table:: Action Summary
   :header-rows: 1
   :widths: 35 30 20 15

   * - Action Name
     - Type
     - Server Node
     - Status
   * - ``/movensys_manipulator_arm_controller/follow_joint_trajectory``
     - ``control_msgs/action/FollowJointTrajectory``
     - ``joint_trajectory_controller``
     - Active

FollowJointTrajectory
----------------------

.. list-table::
   :widths: 25 75

   * - **Action Name**
     - ``/movensys_manipulator_arm_controller/follow_joint_trajectory``
   * - **Action Type**
     - ``control_msgs/action/FollowJointTrajectory``
   * - **Server Node**
     - ``joint_trajectory_controller``
   * - **Configurable**
     - Name set via ``joint_trajectory_action`` parameter
   * - **Source File**
     - ``joint_trajectory_controller.cpp``

This action server receives a joint-space trajectory (a sequence of waypoints
with timestamps) and executes it on the physical robot using the WMX
``AdvancedMotion::StartCSplinePos()`` cubic spline interpolation engine.

Goal
^^^^^

The goal uses the standard ``trajectory_msgs/msg/JointTrajectory`` message:

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Field
     - Type
     - Description
   * - ``trajectory.joint_names``
     - ``string[]``
     - Joint names (``joint1`` through ``joint6``)
   * - ``trajectory.points[]``
     - ``JointTrajectoryPoint[]``
     - Ordered list of waypoints (maximum **1000 points**)
   * - ``trajectory.points[].positions``
     - ``float64[]``
     - Target joint positions in radians for each waypoint
   * - ``trajectory.points[].time_from_start``
     - ``duration``
     - Timestamp relative to trajectory start

.. note::

   Only the ``positions`` and ``time_from_start`` fields of each trajectory
   point are used. The ``velocities``, ``accelerations``, and ``effort``
   fields are logged and discarded -- the WMX C-spline derives the profile
   from the position/time sequence itself.

**Joint mapping.** When the goal carries ``joint_names``, each goal column is
matched to its axis by name against the ``joint_name`` parameter. A goal that
names an unknown joint, repeats one, or leaves one out is **rejected**. Only
when ``joint_name`` is left empty does the server fall back to positional
mapping, and it warns about that at startup.

Result
^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Field
     - Type
     - Description
   * - ``error_code``
     - ``int32``
     - ``0`` on success; WMX error code on failure
   * - ``error_string``
     - ``string``
     - Not set by the server (default empty)

``error_code`` is the raw WMX error code on a motion failure, and
``GOAL_TOLERANCE_VIOLATED`` when the goal outruns its deadline (see below).

Feedback
^^^^^^^^^

No feedback messages are published during execution, and there is no path
tolerance or goal tolerance check beyond the deadline described below. Watch
``/joint_states`` or ``/wmx/axes/status`` if you need progress.

Execution Details
^^^^^^^^^^^^^^^^^^

The server processes the trajectory as follows:

1. **Goal acceptance** -- A goal is **rejected** if the node is not
   ``active``, if another goal is already running, or if its ``joint_names``
   do not map cleanly onto ``joint_name``. Accepted goals run
   ``ACCEPT_AND_EXECUTE``.

2. **Thread dispatch** -- ``execute()`` runs on one execution thread that the
   node owns and joins, so no goal outlives the WMX device handle. The action
   server stays responsive while a goal runs.

3. **Validation** -- A goal with more than **1000** points is aborted with no
   motion. ``MAX_TRAJ_POINTS`` is a compile-time constant, not a parameter: it
   sizes the WMX spline buffer allocated at ``configure``.

4. **Timing adjustment** -- The first point's ``time_from_start`` is forced to
   zero. A final point less than 1 ms after its predecessor is dropped;
   planners routinely emit such a duplicate endpoint.

5. **Spline construction** -- Positions are packed into a ``CSplinePosData``
   structure with timestamps in milliseconds. ``dimensionCount`` and the
   ``axis[]`` array come from the ``joint_axes`` parameter.

6. **Execution** -- ``AdvancedMotion::StartCSplinePos(0, ...)`` starts the
   interpolated motion on buffer 0 across all joints at once. A WMX error
   aborts the goal with ``error_code`` set to the raw WMX code.

7. **Wait, then poll** -- The server first waits out the planned duration of
   the trajectory, taken from the last ``time_from_start``, then polls every
   10 ms until **both** ``motionComplete`` and ``inPos`` are set on every
   ``joint_axes`` entry. Because it waits out the planned duration, a goal
   cannot report success before the motion has had time to run.

8. **Deadline** -- A goal that has not finished **10 s past** its planned
   duration is stopped and aborted with ``GOAL_TOLERANCE_VIOLATED``.

9. **Exit** -- On every exit path -- success, abort, or cancel -- the server
   publishes ``execution_active: false`` and a zero-velocity ``JointJog`` on
   ``/servo_node/delta_joint_cmds``, so MoveIt Servo does not resume with a
   stale delta.

.. note::

   Cancellation is supported. ``handle_cancel()`` accepts the request and the
   polling loop checks ``is_canceling()`` each iteration -- on cancel it calls
   ``CoreMotion::Stop()`` then ``Wait()``, reports ``error_code = 0``, and
   marks the goal ``canceled``.

.. note::

   Deactivating the controller destroys the action server, so no new goal can
   arrive. A goal already running sees the deactivation, stops the axes, and
   aborts; ``on_deactivate`` waits for it.

Arbitration with MoveIt Servo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``joint_trajectory_controller`` (planned motion) and
``joint_position_controller`` (streamed servo motion) command the same axes,
so they interlock over ``/moveit2_trajectory/execution_active``:

.. mermaid::
   :caption: Planned versus streamed motion

   sequenceDiagram
       participant MG as MoveIt2 move_group
       participant JTC as joint_trajectory_controller
       participant JPC as joint_position_controller
       participant SV as MoveIt Servo

       MG->>JTC: FollowJointTrajectory goal
       JTC-->>JPC: execution_active = true (latched)
       Note over JPC: drops every streamed trajectory while true
       JTC->>JTC: StartCSplinePos, wait, poll
       JTC-->>MG: succeeded / aborted / canceled
       JTC-->>JPC: execution_active = false
       JTC-->>SV: zero JointJog on /servo_node/delta_joint_cmds

The latch is one-directional: a servo motion already in flight is **not**
preempted when a planned goal starts. Pause MoveIt Servo, or accept that the
first goal wins the race, if both can be commanded at once.

Example Usage
^^^^^^^^^^^^^^

**Send a simple two-point trajectory via the command line:**

.. code-block:: bash

   wros ros2 action send_goal \
     /movensys_manipulator_arm_controller/follow_joint_trajectory \
     control_msgs/action/FollowJointTrajectory \
     "{trajectory: {
       joint_names: ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6'],
       points: [
         {positions: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
          time_from_start: {sec: 0, nanosec: 0}},
         {positions: [0.5, -0.3, 0.2, 0.0, 0.1, 0.0],
          time_from_start: {sec: 3, nanosec: 0}}
       ]
     }}"

**Check that the action server is available:**

.. code-block:: bash

   wros ros2 action list

Expected:

.. code-block:: text

   /movensys_manipulator_arm_controller/follow_joint_trajectory

**Inspect the action interface:**

.. code-block:: bash

   wros ros2 action info /movensys_manipulator_arm_controller/follow_joint_trajectory

.. warning::

   This action moves real motors. Before sending trajectory goals, confirm
   that the robot parameters have been verified
   (:doc:`../try_your_robot/robot_parameters`), that the robot has passed the
   first-motion procedure (:doc:`../try_your_robot/first_motion`), that the
   workspace is clear, and that the separate safety measures in
   :doc:`../try_your_robot/safety` are in place. Cancelling a goal is a
   controlled stop, not an emergency stop.

MoveIt2 Integration
^^^^^^^^^^^^^^^^^^^^

MoveIt2 connects to this action server as a trajectory execution controller.
The typical workflow is:

1. MoveIt2 reads the current robot state from ``/joint_states``
2. The planner computes a collision-free trajectory
3. MoveIt2 sends the trajectory as a ``FollowJointTrajectory`` goal
4. The ``joint_trajectory_controller`` executes it via WMX cubic spline
5. The ``joint_state_broadcaster`` node publishes real-time encoder feedback back
   to ``/joint_states`` at 100 Hz

The action server name must match the controller configuration in MoveIt2.
The default name ``/movensys_manipulator_arm_controller/follow_joint_trajectory``
is set via the ``joint_trajectory_action`` parameter in the config YAML.

See Also
^^^^^^^^

- :doc:`ros2_topics` -- ``/joint_states`` topic details
- :doc:`ros2_services` -- ``/wmx/set_gripper`` service (hosted by the
  ``gripper_controller`` node)
- :doc:`../integration/moveit2_integration` -- MoveIt2 setup
