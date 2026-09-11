Robot Parameter Configuration and Validation
============================================

.. warning::

   The parameters on this page decide how far and in which direction each
   joint moves. An incorrect gear ratio, encoder resolution, joint direction,
   or home offset causes unexpected motion even when every node reports
   success. Review and verify all of them in simulation and HIL before
   powering a physical robot. See :ref:`simulation-first-workflow`.

Where the parameters live
-------------------------

A robot configuration is **data, not code**. Everything that makes the stack
drive one machine rather than another lives in four kinds of file, and a
different robot, a different drive brand, or a different axis count is a
change to those files only — no C++ or Python in ``wmx-r2``,
``movensys-manipulator``, or ``movensys-navigation`` is modified, and the
launch files take each file as an argument rather than hard-coding it.

.. list-table::
   :header-rows: 1
   :widths: 38 62

   * - File
     - Defines
   * - **1. ENI file**

       The EtherCAT network description
     - Which slaves are on the bus and how the master communicates with them.
   * - **2. WMX parameter file**

       ``wmx_r2_package/example/<robot>_wmx_parameters.xml``
     - Gear ratio, encoder resolution, polarity, command mode, torque and
       speed limits, homing, and soft limits — per WMX axis index.
   * - **3. URDF / xacro**

       ``movensys_*_description/urdf/<model>/``, ``wmx_r2_control/urdf/``
     - Link geometry, joint axes and origins, the limits used for planning
       and collision checking, and the ``ros2_control`` hardware interface.
   * - **4. ROS 2 parameter YAML**

       ``wmx_r2_package/example/``, ``wmx_r2_control/config/``, and the
       MoveIt, Nav2, and perception ``config/<model>/`` directories
     - Joint name ↔ axis index, feedback rate, topic and action names,
       gripper I/O addresses, and the planner and controller settings.

The ENI is generated from a scan of the real network by the NetConfigurator
app in the WMX web gateway; see :doc:`wmx_web_tools` for the
Scan → Quick Create → Start Communication procedure and for where the
generated ENI is written.

.. note::

   **ESI** files are not on this list. They are the device descriptions the
   drive manufacturer supplies, and they are input to ENI generation rather
   than something you author or edit.

They must agree with each other; nothing in the stack checks that they do.
The rest of this page is about the values inside them and how to verify each
one.

.. note::

   "Only four files" is a statement about *where* the work is, not about how
   much of it there is. Producing a correct parameter set, URDF, and planning
   configuration for a machine nobody has commissioned yet is an integration
   project — see :doc:`validated_hardware`. What it is *not* is a change to
   WMX R2.

.. note::

   The WMX parameter file is applied by the node that owns the **engine**.
   ``wmx_engine_node`` calls ``Config::ImportAndSetAll`` on the path in its
   ``wmx_param_file_path`` parameter right after the device is created; the
   launch files inject that from their ``wmx_param_file`` argument. The
   ``ros2_control`` hardware plugin does the same with the ``wmx_param_file``
   hardware parameter from ``<robot>.wmx.ros2_control.xacro``.

   Paths are normally written as
   ``$(ros2 pkg prefix --share wmx_r2_package)/example/...``, which resolves to
   the **install** space — so an edit to the file in ``src/`` only takes
   effect after a rebuild, or after editing the installed copy.

   To reload without restarting, call ``/wmx/engine/import_and_set_all`` with
   an absolute path.

Mapping between ROS 2 joint names and physical axes
---------------------------------------------------

The ROS 2 joint name is bound to a WMX axis index by position in two lists in
the application YAML — ``joint_name[i]`` is driven by ``joint_axes[i]``:

.. code-block:: yaml

   joint_state_broadcaster:
     ros__parameters:
       joint_axes: [0, 1, 2, 3, 4, 5]
       joint_name: ["joint1", "joint2", "joint3", "joint4", "joint5", "joint6"]

The WMX axis index is in turn the position of the servo drive in the EtherCAT
daisy chain, as discovered by the network scan. The chain order is physical
wiring, not configuration.

.. list-table:: Shipped mapping (CR3A and CR5A)
   :header-rows: 1
   :widths: 20 20 30 30

   * - ROS 2 joint
     - WMX axis
     - EtherCAT position
     - Physical joint
   * - ``joint1``
     - 0
     - 1st drive in the chain
     - Base rotation
   * - ``joint2``
     - 1
     - 2nd drive
     - Shoulder
   * - ``joint3``
     - 2
     - 3rd drive
     - Elbow
   * - ``joint4``
     - 3
     - 4th drive
     - Wrist 1
   * - ``joint5``
     - 4
     - 5th drive
     - Wrist 2
   * - ``joint6``
     - 5
     - 6th drive
     - Wrist 3

For the differential-drive base, ``diffbot_differential_config.yaml`` binds the
axes twice — once for feedback and once for the drive controller — and both
must agree:

.. code-block:: yaml

   differential_drive_controller:
     ros__parameters:
       left_axis: 0
       right_axis: 1

   joint_state_broadcaster:
     ros__parameters:
       joint_axes: [0, 1]
       joint_name: ["drivewheel_left_joint", "drivewheel_right_joint"]

.. warning:: **Verify the mapping physically, one axis at a time.**

   Nothing in the stack detects a swapped mapping. If two drives are chained
   in an order different from the one assumed here, commanding ``joint2`` will
   move a different physical joint, and the planner's collision checking will
   be reasoning about the wrong link. Confirm the mapping with the single-axis
   jog procedure in :doc:`first_motion` before enabling multi-axis motion.

Encoder resolution and unit conversion
---------------------------------------

WMX works in *user units*. The conversion from encoder counts to user units is
the axis gear ratio:

.. code-block:: text

   AxisGearRatioNumerator     encoder counts per revolution of the joint output
   ─────────────────────── =  ────────────────────────────────────────────────
   AxisGearRatioDenominator                 user units per revolution

Every shipped parameter file sets:

.. code-block:: xml

   <AxisGearRatioDenominator>6.283185307179586</AxisGearRatioDenominator>

That denominator is 2π, which makes **one WMX user unit equal to one radian**.
This is the only reason the ROS 2 interface can pass positions straight
through: ``joint_state_broadcaster`` publishes ``actualPos`` into
``/joint_states`` with no scaling, ``/wmx/axes/start_pos`` targets are
consumed as radians, and ``joint_trajectory_controller`` writes goal positions
straight into the WMX C-spline.

.. important::

   The "radians" stated throughout the :doc:`../api_reference/api_reference`
   are a *consequence* of ``AxisGearRatioDenominator = 2π``, not a property of
   the software. If you author a parameter file with a different denominator,
   every position, velocity, and acceleration on every WMX topic and service
   silently changes units, and the joint states published to MoveIt or Nav2
   become wrong by that factor.

The numerator is the number of encoder counts in one full revolution of the
**joint output**, which is the motor encoder resolution multiplied by the gear
ratio:

.. code-block:: text

   AxisGearRatioNumerator = encoder counts per motor revolution × gear ratio

Gear ratios and encoder resolution — shipped values
----------------------------------------------------

.. list-table:: ``cr3a_wmx_parameters.xml``
   :header-rows: 1
   :widths: 14 12 26 22 26

   * - ROS 2 joint
     - WMX axis
     - ``AxisGearRatioNumerator``
     - Counts per rad
     - Consistent with
   * - ``joint1``
     - 0
     - 52 953 088
     - 8 427 746
     - 2\ :sup:`19` counts × 101:1
   * - ``joint2``
     - 1
     - 52 953 088
     - 8 427 746
     - 2\ :sup:`19` counts × 101:1
   * - ``joint3``
     - 2
     - 42 467 328
     - 6 758 885
     - 2\ :sup:`19` counts × 81:1
   * - ``joint4``
     - 3
     - 42 467 328
     - 6 758 885
     - 2\ :sup:`19` counts × 81:1
   * - ``joint5``
     - 4
     - 42 467 328
     - 6 758 885
     - 2\ :sup:`19` counts × 81:1
   * - ``joint6``
     - 5
     - 42 467 328
     - 6 758 885
     - 2\ :sup:`19` counts × 81:1

``cr5a_wmx_parameters.xml`` uses the same two values with a different split:
axes 0, 1, and 2 use 52 953 088; axes 3, 4, and 5 use 42 467 328.

``diffbot_wmx_parameters.xml`` uses 4 915 200 counts per wheel revolution on
both drive axes (782 278 counts per radian), consistent with a
2\ :sup:`16`-count encoder and a 75:1 reduction.

.. note::

   The "consistent with" column is a factorization of the shipped numerator,
   not a value read from the drive. Confirm the encoder resolution and the
   reducer ratio against your drive's datasheet and the robot's mechanical
   specification — a numerator that is wrong by the reducer ratio produces
   motion that is wrong by roughly two orders of magnitude.

Joint direction and sign conventions
-------------------------------------

``AxisPolarity`` inverts the direction of both the command and the feedback
for one axis. It takes ``+1`` or ``-1``. The shipped values differ per robot
because the motors are mounted in different orientations:

.. list-table:: ``AxisPolarity`` by axis
   :header-rows: 1
   :widths: 28 12 12 12 12 12 12

   * - Parameter file
     - ax 0
     - ax 1
     - ax 2
     - ax 3
     - ax 4
     - ax 5
   * - ``cr3a_wmx_parameters.xml``
     - −1
     - −1
     - +1
     - −1
     - −1
     - −1
   * - ``cr5a_wmx_parameters.xml``
     - +1
     - +1
     - +1
     - +1
     - +1
     - +1
   * - ``diffbot_wmx_parameters.xml``
     - −1
     - −1
     -
     -
     -
     -

The sign convention that ``AxisPolarity`` has to satisfy is set by the URDF:
each joint's ``<axis xyz="…"/>`` and the parent ``<origin rpy="…"/>`` together
define which physical rotation is positive. On the differential-drive base,
for example, the two wheel joints are mirrored — the left wheel has
``rpy="-1.57 0 0"`` with ``axis xyz="0 0 1"`` and the right wheel
``rpy="1.57 0 0"`` with ``axis xyz="0 0 -1"`` — so a naive "both wheels
forward" assumption about the drives is not enough.

.. warning::

   Polarity is the single most common cause of a robot that runs away on its
   first commanded move. With the wrong sign, a closed-loop correction drives
   the joint further from the target instead of toward it. Verify polarity one
   axis at a time, at low speed, with a small step, using the procedure in
   :doc:`first_motion`.

Home positions and encoder offsets
-----------------------------------

All three shipped parameter files use absolute encoders and no offset:

.. list-table::
   :header-rows: 1
   :widths: 34 16 50

   * - Parameter
     - Shipped
     - Meaning
   * - ``AbsoluteEncoderMode``
     - ``1``
     - Absolute encoder. Position is known at power-on; no homing move is
       required.
   * - ``AbsoluteEncoderHomeOffset``
     - ``0.0``
     - Offset added to the raw absolute position. ``0`` means the ROS 2 zero
       for the joint is exactly the drive's absolute zero.
   * - ``HomePosition`` (``HomeParam``)
     - ``0.0``
     - Position written to the axis when a homing sequence completes.
   * - ``HomeType`` / ``HomeDir``
     - ``0`` / ``0``
     - Homing method and direction. Unused while the absolute encoder supplies
       the position.
   * - ``ClearHomeDoneOnCommStop``
     - ``1``
     - The "home done" flag is cleared when EtherCAT communication stops.

.. important::

   ``AbsoluteEncoderHomeOffset = 0`` is a claim about **your** robot's
   mechanical zero, not a safe default. It asserts that the drive's absolute
   zero coincides with the zero pose in the URDF. If your robot's encoders
   were zeroed at a different mechanical position — a replaced motor, a
   re-indexed reducer, a different build of the same model — this value is
   wrong and every joint will be offset by a constant. Verify it by moving
   each joint to a known mechanical reference and comparing the reported
   position (see :doc:`first_motion`).

Position, velocity, and acceleration limits
--------------------------------------------

Limits are enforced in more than one place, and the shipped configuration does
**not** enforce position limits in the motion engine.

.. list-table::
   :header-rows: 1
   :widths: 24 26 50

   * - Limit
     - Where it is enforced
     - Shipped configuration
   * - Joint position
     - URDF ``<limit lower= upper=>`` — checked by MoveIt during planning
     - CR3A: ``joint1`` ±3.0, ``joint2`` −1.57…1.1, ``joint3`` −2.55…0.2,
       ``joint4`` ±2.5, ``joint5`` −0.1…3.0, ``joint6`` ±3.0 rad.

       CR5A: ``joint1`` −1.57…4.71239, ``joint2`` ±1.57, ``joint3``
       −0.2…2.55, ``joint4`` ±2.5, ``joint5`` −3.14…0.1, ``joint6`` ±3.14 rad.
   * - Joint position (engine)
     - WMX ``SoftLimitType`` in ``LimitParam``
     - **Disabled** (``SoftLimitType = 0``, both soft-limit positions ``0.0``)
       on every axis of every shipped file.
   * - Joint velocity
     - URDF ``velocity`` attribute; MoveIt ``joint_limits.yaml``
     - URDF: 3.0 rad/s (both arms). MoveIt: CR3A 2.0 rad/s, CR5A 1.0 rad/s —
       the MoveIt value is the one that bounds planned trajectories.
   * - Joint acceleration
     - MoveIt ``joint_limits.yaml``
     - CR3A 2.0 rad/s², CR5A 1.0 rad/s². Not expressed in the URDF.
   * - Motor speed
     - WMX ``MaxMotorSpeed``
     - 3000 rpm on every axis.
   * - Torque
     - WMX ``MaxTrqLimit`` / ``PositiveTrqLimit`` / ``NegativeTrqLimit``
     - 300 (% of rated) on every axis.
   * - Deceleration on stop
     - WMX ``QuickStopDec`` and ``EStopDec``
     - 100 000 user units/s² (rad/s²) on every axis.

.. warning:: **Soft limits are off in the shipped parameter files.**

   With ``SoftLimitType = 0``, the WMX engine will accept and execute a
   position command outside the robot's mechanical range. The only thing
   keeping motion inside the joint limits is MoveIt's planning-time check
   against the URDF — which does not apply to direct ``/wmx/axes/start_pos``
   commands, to ``keyboard_teleop`` jogging, or to anything else that
   bypasses the planner.

   Before running a physical robot, either enable WMX soft limits with the
   mechanical range of your robot, or treat every direct axis command as
   unbounded and hold to the low-speed, small-step procedure in
   :doc:`first_motion`.

EtherCAT axis mapping
---------------------

The WMX axis index is assigned by the EtherCAT network scan in daisy-chain
order, so it follows the wiring. Confirm the discovered network before
trusting any axis index:

.. code-block:: bash

   wros ros2 service call /wmx/ecat/get_master_info \
        wmx_r2_message/srv/EcatGetMasterInfo "{master_id: 0}"

The scan matches each discovered slave against the EtherCAT Slave
Information (ESI) files installed with the WMX Runtime at ``/opt/wmx3/ESI/``,
and the network as a whole is described by the EtherCAT Network Information
(ENI) file, generated from a scan by **NetConfigurator → ENI File →
Quick Create** and written to the folder named by that app's **Eni Folder**
setting (see :doc:`wmx_web_tools`). A
drive with no matching ESI file will fail the scan, and a chain that is
re-cabled in a different order shifts every axis index after the change —
silently, from ROS 2's point of view.

The gripper I/O module is part of the same chain. Its bit addresses are
configured separately in the application YAML, not by axis index:

.. code-block:: yaml

   gripper_controller:
     ros__parameters:
       gripper_address: [0, 0]      # [byte, bit] of the gripper output

Consistency between URDF, MoveIt, and WMX
------------------------------------------

Each row below is a value that appears in more than one file. All of them have
to agree, and none of them is checked automatically.

.. list-table::
   :header-rows: 1
   :widths: 26 37 37

   * - Must agree
     - Source A
     - Source B
   * - Joint names
     - URDF ``<joint name=…>``
     - ``joint_name`` in the application YAML, and the joint names in the
       SRDF planning group
   * - Joint count and order
     - ``joint_axes`` in the application YAML
     - The number of ``<joint>`` entries in
       ``<robot>.wmx.ros2_control.xacro``, each with its ``axis`` parameter
   * - Rotation direction
     - URDF ``<axis xyz>`` plus the joint ``<origin rpy>``
     - ``AxisPolarity`` in the WMX parameter file
   * - Units
     - URDF (radians, by ROS convention)
     - ``AxisGearRatioDenominator = 2π`` in the WMX parameter file
   * - Zero pose
     - URDF zero configuration
     - ``AbsoluteEncoderHomeOffset`` and ``HomePosition``
   * - Velocity limits
     - URDF ``velocity`` attribute
     - MoveIt ``joint_limits.yaml`` ``max_velocity``
   * - Wheel geometry (diffbot)
     - URDF wheel ``<cylinder radius>`` = 0.095 m and wheel joint origins
       ``y = ±0.275`` m
     - ``wheel_radius: 0.095`` and ``wheel_to_wheel: 0.55`` in
       ``diffbot_differential_config.yaml``

Source of each parameter, and how to verify it
-----------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 26 36 38

   * - Parameter
     - Where the value comes from
     - How to verify
   * - Joint ↔ axis mapping
     - EtherCAT wiring order, recorded in the application YAML
     - Jog one axis at a time and watch which physical joint moves
       (:doc:`first_motion`)
   * - Encoder resolution
     - Servo drive / motor datasheet
     - Command one full revolution of the motor and compare the count delta
       reported by ``/wmx/axes/status``
   * - Gear ratio
     - Robot mechanical specification (reducer ratio per joint)
     - Command a known joint angle and measure the physical rotation with an
       inclinometer or a marked reference
   * - Joint direction
     - URDF axis convention plus the motor mounting orientation
     - Command a small positive step; confirm the joint moves in the URDF's
       positive direction and that RViz agrees with the physical robot
   * - Home offset
     - Robot mechanical zero versus drive absolute zero
     - Move each joint to a known mechanical reference and compare the
       reported position
   * - Position limits
     - Robot mechanical specification
     - Compare against the URDF; approach each end of travel at low speed
   * - Velocity / acceleration limits
     - Application requirement, bounded by the drive and mechanics
     - Time a known move and compare against the commanded profile
   * - Torque limits
     - Motor rated torque and the robot's payload rating
     - Read ``actual_torque`` from ``/wmx/axes/status`` during a representative
       move

Reading back what the engine actually loaded
---------------------------------------------

The values that matter are the ones in the running engine, not the ones in the
file. Two mechanisms expose them.

**1. The parameter dump service.** ``/wmx/engine/get_axis_param`` returns the gear ratio,
axis unit, polarity, command mode, torque limits, motor speed, and the homing
parameters that the engine currently holds, per axis:

.. code-block:: bash

   wros ros2 service call /wmx/engine/get_axis_param wmx_r2_message/srv/GetAxisParam \
        "{axis: [0,1,2,3,4,5]}"

Compare the ``GearRatio``, ``AxisPolarity``, and ``CommandMode`` lines in the
response against the table you built for your robot. This is the definitive
check — it reflects the engine state after the parameter file was applied.

**2. The broadcaster startup log.** At ``configure``,
``joint_state_broadcaster`` calls ``/wmx/engine/get_axis_param`` for its own
``joint_axes`` and logs the dump at INFO, so the axis setup a run actually
used is captured in the startup log. A missing engine service only warns —
configuration still succeeds, so an empty dump is not an error you will see
as a failure.

``wmx_engine_node`` logs the result of importing ``wmx_param_file`` at engine
start. If the import fails, it logs the failing field.

.. note::

   A successful import means the file was syntactically valid and accepted by
   the engine. It says nothing about whether the values describe your robot.

Changing parameters at runtime
-------------------------------

Two services change axis parameters without editing the file. Both take effect
immediately on a live engine.

.. code-block:: bash

   # Load a different parameter file wholesale
   wros ros2 service call /wmx/engine/import_and_set_all wmx_r2_message/srv/ImportAndSetAll \
        "{path: '/abs/path/to/<robot>_wmx_parameters.xml'}"

   # Override the gear ratio on selected axes
   wros ros2 service call /wmx/axes/set_gear_ratio \
        wmx_r2_message/srv/SetAxesGearRatio \
        "{axis: [0], numerator: [52953088.0], denominator: [6.283185307179586]}"

   # Override the polarity on selected axes (+1 or -1)
   wros ros2 service call /wmx/axes/set_axis_polarity wmx_r2_message/srv/SetAxes \
        "{axis: [0], data: [-1]}"

.. warning::

   Changing a gear ratio or polarity while an axis is enabled changes the
   meaning of the current position and of every subsequent command. Do this
   only with the axis stopped, and re-verify with a low-speed single-axis jog
   afterwards. Runtime overrides are not written back to the XML file — they
   are lost on the next engine restart, which means a robot that behaved
   correctly during a tuning session can behave differently after a reboot.
