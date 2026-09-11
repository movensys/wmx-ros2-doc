Hardware Compatibility and Validation
=====================================

.. important:: **"Any EtherCAT machine" is about the software, not about**
   **what has been validated.**

   WMX R2 controls axes over EtherCAT CoE rather than a specific robot model,
   and moving it to a new machine changes only configuration files — see
   :doc:`index`. That is a real property of the stack, and it is not the same
   thing as the machine being ready to run.

   Whether WMX R2 can drive *your* robot today depends on whether the drives
   speak EtherCAT CoE in a supported mode, whether a matching ESI file is
   installed for them and an EtherCAT Network Information (ENI) file exists
   for the network, and whether someone has produced and verified a correct
   parameter set, URDF, and planning configuration for that specific machine.

   The robots below are the ones for which this project ships and has verified
   that configuration. For anything else the files exist but their contents do
   not yet — producing and validating them is an integration project.

Status definitions
------------------

.. list-table::
   :header-rows: 1
   :widths: 24 76

   * - Status
     - Meaning
   * - **Validated**
     - Run on the physical robot by MOVENSYS. A verified parameter file,
       URDF, and application configuration are shipped, and the listed
       functions were exercised on hardware.
   * - **Reference implementation**
     - A complete, shipped configuration that is exercised in simulation and
       HIL. Treat the hardware parameters as a starting point to be verified
       per unit, following :doc:`robot_parameters` and :doc:`first_motion`.
   * - **Experimental**
     - Present in the repository but incomplete, unverified, or subject to
       change. Not intended for use on a physical robot.
   * - **Not supported**
     - No shipped configuration. Requires an integration project.

.. note::

   Status applies to a *robot model plus a function*, not to a robot model
   alone. A model validated for trajectory execution is not thereby validated
   for perception-driven picking.

Robot matrix
------------

.. list-table::
   :header-rows: 1
   :widths: 20 12 14 18 36

   * - Robot
     - Axes
     - Status
     - Parameter file
     - Notes
   * - **Dobot CR3A**
     - 6 + gripper
     - Validated
     - ``cr3a_wmx_parameters.xml``
     - The reference platform. Trajectory, gripper, AprilTag, YOLO, Nvblox,
       and the Robopoly application are all configured for this arm.
   * - **Dobot CR5A**
     - 6
     - Validated (trajectory only)
     - ``cr5a_wmx_parameters.xml``
     - Trajectory execution and keyboard/Servo jogging only. No gripper and
       no perception configuration is shipped — see the function matrix.
   * - **Differential-drive base** (``diffbot``)
     - 2
     - Validated
     - ``diffbot_wmx_parameters.xml``
     - Velocity-mode axes (``AxisCommandMode = 1``) driven by
       ``differential_drive_controller``, with Nav2, EKF, and SLAM Toolbox.

Function matrix
---------------

.. list-table::
   :header-rows: 1
   :widths: 34 22 22 22

   * - Function
     - Dobot CR3A
     - Dobot CR5A
     - diffbot
   * - General nodes (engine, axis, I/O, EtherCAT)
     - Validated
     - Validated
     - Validated
   * - Joint state feedback
     - Validated
     - Validated
     - Validated
   * - ``FollowJointTrajectory`` execution
     - Validated
     - Validated
     - —
   * - MoveIt 2 (OMPL) planning
     - Validated
     - Validated
     - —
   * - Isaac cuMotion planning
     - Validated
     - Not configured
     - —
   * - MoveIt Servo / keyboard jogging
     - Validated
     - Reference implementation
     - —
   * - ``ros2_control`` hardware interface
     - Reference implementation
     - Reference implementation
     - Reference implementation
   * - Gripper (digital I/O)
     - Validated
     - Not configured
     - —
   * - AprilTag pick and place
     - Validated
     - Not configured
     - —
   * - YOLO pick and place
     - Validated
     - Not configured
     - —
   * - Nvblox obstacle avoidance
     - Validated
     - Not configured
     - —
   * - Robopoly (VLM/LLM application)
     - Validated
     - Not configured
     - —
   * - Nav2 autonomous navigation
     - —
     - —
     - Validated
   * - SLAM mapping
     - —
     - —
     - Validated
   * - Manual teleoperated driving
     - —
     - —
     - Validated

.. note::

   "Not configured" means the repository ships no configuration for that
   combination — the launch will fail to find its config file rather than run
   with a wrong one. For the CR5A this covers everything under
   ``movensys_manipulator_perception/config/`` and
   ``movensys_manipulator_isaac_ros_config/config/``, and for the diffbot this covers everything under
   ``movensys_navigation/config/``.

Homing, absolute position, brakes, and safety
-----------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 24 76

   * - Topic
     - Handling
   * - **Homing**
     - Not used on any shipped robot. ``AbsoluteEncoderMode = 1`` on every
       axis, so position is known at power-on. The homing service
       (``/wmx/axes/start_home``) and the ``HomeParam`` block exist and are
       populated with defaults, but no shipped configuration exercises them.
       A robot with incremental encoders requires a homing strategy that this
       project does not provide.
   * - **Absolute position**
     - ``AbsoluteEncoderHomeOffset = 0.0`` on every shipped axis, asserting
       that the drive's absolute zero is the URDF zero. **Verify this per
       unit** — it is a property of the individual robot, not of the model.
       See :doc:`robot_parameters`.
   * - **Brakes**
     - Not managed by WMX R2. Brake release and engagement are handled by the
       drive and the robot's electrical design. Brake behavior on power loss
       and on emergency stop must be covered by the system risk assessment.
   * - **Safety systems**
     - None are provided. WMX R2 is not safety-rated, and the safety
       functions of the robot manufacturer's original controller are not
       available when that controller is bypassed. See :doc:`safety`.
   * - **Soft limits**
     - Disabled (``SoftLimitType = 0``) in all three shipped parameter files.
       Position limiting exists only in MoveIt's planning-time check against
       the URDF.
   * - **E-stop input**
     - ``EnableEStopSignal = 0`` in all three shipped parameter files. The
       WMX engine's E-stop input is not configured, and is in any case a
       functional input rather than a safety function.

Validated parameter files
--------------------------

The parameter files shipped in ``wmx_r2_package/example/`` are the starting
point for the corresponding robot model:

.. list-table::
   :header-rows: 1
   :widths: 34 30 36

   * - File
     - Robot
     - Application config
   * - ``cr3a_wmx_parameters.xml``
     - Dobot CR3A
     - ``cr3a_manipulator_config.yaml``
   * - ``cr5a_wmx_parameters.xml``
     - Dobot CR5A
     - ``cr5a_manipulator_config.yaml``
   * - ``diffbot_wmx_parameters.xml``
     - Differential-drive base
     - ``diffbot_differential_config.yaml``

.. warning::

   A shipped parameter file describes the robot MOVENSYS commissioned. It is
   not a guarantee for your unit. Encoder zero, motor mounting orientation,
   reducer ratio after a repair, and mechanical range can all differ between
   units of the same model. Re-run :doc:`first_motion` on every physical
   robot, including a second unit of an already-validated model.

.. _bringing-up-an-unlisted-robot:

Bringing up a robot that is not listed
----------------------------------------

There is no supported path that consists only of editing configuration. At
minimum you need:

1. **EtherCAT compatibility.** Drives reachable by the WMX EtherCAT master,
   with a matching ESI file in ``/opt/wmx3/ESI/`` for each slave, in a
   supported CoE mode (position mode for the manipulators, velocity mode for
   the differential-drive base).
2. **A parameter file.** Gear ratio numerator and denominator, polarity,
   command mode, and limits for every axis, derived from the drive and
   mechanical specifications — see :doc:`robot_parameters`.
3. **A URDF.** Link geometry, joint axes and origins, and position, velocity,
   and effort limits, consistent with the parameter file.
4. **A planning configuration.** SRDF, kinematics, joint limits, and
   controller configuration for MoveIt 2, or the equivalent Nav2
   configuration for a mobile base.
5. **An application YAML.** The joint-name to axis-index mapping and the
   topic, action, and I/O configuration.
6. **Full commissioning.** The complete :ref:`simulation-first-workflow`,
   with the safety architecture in :doc:`safety` in place first.

Contact your MOVENSYS representative before starting an integration for a
robot that is not listed above.
