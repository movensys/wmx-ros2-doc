Safety Functions and Responsibility
===================================

.. danger:: **WMX R2 replaces the robot manufacturer's controller. It does not
   replace that controller's safety functions.**

   WMX R2 is designed to control the servo system *without* using the robot
   manufacturer's original controller. The safety-related functions that
   controller normally provides — the functions an industrial robot controller
   is required to implement under ISO 10218-1 — are supplied by that
   controller's hardware and certified safety logic. When you bypass it, those
   functions are **no longer available**, regardless of how WMX R2 is
   configured.

   Neither WMX R2 nor the WMX motion engine is a safety-rated product. Nothing
   in this stack is certified to ISO 10218-1, ISO 13849-1, or IEC 62061, and
   no part of it may be used to implement a safety function.

What is lost when the original controller is bypassed
------------------------------------------------------

An industrial robot controller certified to ISO 10218-1 typically implements
safety functions in dedicated, redundant, monitored hardware. The list below
is representative rather than exhaustive; the exact set depends on the robot.
Assume that **every** one of them is absent unless you have provided it
yourself.

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Function normally provided
     - Status under WMX R2
   * - Emergency stop (IEC 60204-1 stop category 0 or 1)
     - Not provided. Must be a separate hardwired circuit.
   * - Protective stop / safeguarded-space inputs
     - Not provided.
   * - Safety-rated monitored stop
     - Not provided.
   * - Safety-rated reduced speed (e.g. the 250 mm/s manual-mode limit)
     - Not provided. Speed limits in this stack are planning-time software
       values with no monitoring.
   * - Safety-rated soft axis and space limiting
     - Not provided. See the note on soft limits below.
   * - Speed and separation monitoring
     - Not provided.
   * - Power and force limiting
     - Not provided. WMX torque limits are functional, not safety-rated.
   * - Enabling device / three-position switch
     - Not provided.
   * - Single point of control
     - Not enforced. Any ROS 2 node with access to the topic can command
       motion.
   * - Brake control and brake testing
     - Not provided by this stack. Brakes are handled by the drive and the
       robot's wiring.
   * - Safe stop on loss of communication
     - Not provided as a safety function. The differential-drive controller
       has a functional ``cmd_vel_timeout``; the manipulator path relies on
       Servo's ``incoming_command_timeout``. Both are software timers.

.. warning:: **The functional protections in the shipped configuration are
   weaker than they look, and several are switched off.**

   - ``EnableEStopSignal`` is ``0`` in the global section of every shipped
     parameter file, so the WMX engine's E-stop input is not configured. Even
     when enabled, that input is a functional input to the motion engine — do
     not treat it as a safety function.
   - ``SoftLimitType`` is ``0`` on every axis of every shipped parameter file,
     so the engine does not limit position at all. Position limiting exists
     only in MoveIt's planning-time check against the URDF, which does not
     apply to direct axis commands.
   - MoveIt Servo's collision checking, singularity scaling, and joint-limit
     margins are functional software features running in a non-real-time
     process against a modelled scene. They do not detect anything that is not
     in the planning scene.
   - ``q`` and ``Ctrl+C`` in ``keyboard_teleop`` terminate a process. They do
     not remove power. See :ref:`keyboard-jogging-behavior`.

What a physical system requires instead
----------------------------------------

A WMX R2 installation on physical hardware needs its own safety architecture,
independent of the ROS 2 stack and of the PC running it.

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Measure
     - Notes
   * - **Emergency stop**
     - Hardwired, self-monitoring, reachable from every operating position,
       and independent of the control PC, the operating system, and the ROS 2
       middleware. Implemented to the stop category (IEC 60204-1 category 0 or
       1) that the risk assessment requires.
   * - **STO (Safe Torque Off)**
     - The drive-level mechanism that removes torque-producing power
       (IEC 61800-5-2). Wire the drives' STO inputs into the safety circuit;
       do not rely on a software servo-off command.
   * - **Safety PLC or safety relay**
     - Evaluates the E-stop, guard interlocks, and any safety sensors, and
       drives STO and the brake and contactor outputs. This is where the
       safety logic lives — not in the ROS 2 nodes and not in the WMX engine.
   * - **Brakes**
     - Holding brakes to keep gravity-loaded axes in place when power is
       removed. Include brake behavior on power loss in the risk assessment,
       and verify holding capability with the actual payload.
   * - **Guards and interlocks**
     - Physical guarding, interlocked access doors, light curtains, or
       scanners as appropriate to the layout, with interlocks routed through
       the safety PLC or relay.
   * - **System-level risk assessment**
     - Performed for the complete installation — robot, tooling, payload,
       workspace, and tasks — following ISO 12100, with the integrated system
       addressed under ISO 10218-2. Collaborative operation additionally
       involves ISO/TS 15066. The required performance level or SIL comes out
       of this assessment (ISO 13849-1 / IEC 62061) and determines the
       architecture of everything above.

.. note::

   These are the categories of measure a system needs, not a design. The
   specific implementation, the required performance level, and validation are
   determined by your risk assessment and by the regulations that apply where
   the machine is placed in service.

Responsibility
--------------

- WMX R2 and the WMX motion engine provide **motion control**, not functional
  safety.
- Following this documentation does not by itself produce safe or expected
  motion on physical hardware. Robot-specific parameters must be verified —
  see :doc:`robot_parameters` and :doc:`first_motion`.
- The organization that integrates WMX R2 into a physical machine is the party
  responsible for the risk assessment, the safety architecture, its
  validation, and conformity of the resulting machine.
- The MIT license covering the ROS 2 interface source code disclaims all
  warranties, including fitness for a particular purpose. See :doc:`../licensing`.

Roadmap for safety-related material
------------------------------------

Planned work in this area is documentation and reference material. It is
deliberately **not** a commitment to provide safety functionality equivalent
to a certified industrial robot controller — that would require safety-rated
hardware and third-party certification, which are outside the scope of a ROS 2
interface and a software motion engine.

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Planned
     - Description
   * - Recommended safety architectures
     - Reference block diagrams for typical WMX R2 installations, showing
       where the E-stop, safety PLC, STO, contactors, and brakes sit relative
       to the control PC and the EtherCAT chain.
   * - STO integration examples
     - Worked wiring and configuration examples for connecting drive STO
       inputs to a safety relay and to a safety PLC.
   * - Safety PLC integration examples
     - Examples of interlock and stop-category handling alongside a WMX R2
       control PC, including what the ROS 2 stack should and should not
       observe about safety state.
   * - Commissioning guidance
     - Extension of :doc:`first_motion` with per-robot checklists and
       acceptance criteria.

.. note::

   Dates for these items are not published here. Contact your MOVENSYS
   representative for the current schedule.
