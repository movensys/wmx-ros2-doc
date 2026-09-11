Try Your Robot
==============

.. warning:: **Read this before moving a physical robot.**

   WMX R2 drives servo drives directly over EtherCAT. It does not use the robot
   manufacturer's original controller, so the parameters that decide *how far*
   and *in which direction* a joint moves come from files in this stack, not
   from the robot vendor's firmware.

   A wrong gear ratio, encoder resolution, joint direction, or home offset
   produces unexpected motion **even when every piece of software is working
   correctly**. Following the instructions in this documentation does not by
   itself guarantee safe or expected motion on physical hardware. You must
   verify every robot-specific parameter and put your own safety measures in
   place before operating a physical system. See :doc:`safety` for what those
   measures are and who is responsible for them.

This section covers everything between "the software is installed" and "the
robot moves the way you intended": configuring and validating the
robot-specific parameters, bringing the first axis to life at low speed, and
understanding which safety functions this stack does and does not provide.

What changes when the robot changes
-----------------------------------

WMX R2 controls axes over EtherCAT CoE, not a specific robot model, so the
packages themselves are the same on every machine. Commissioning a different
robot, a different drive brand, or a different axis count is a change to four
kinds of file — and to no source code:

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - File
     - Carries
   * - **ENI file**

       The EtherCAT network description
     - Which slaves are on the bus and how the master communicates with them.
       Generated from a scan of the real network by NetConfigurator; see
       :doc:`wmx_web_tools`.
   * - **WMX parameter file**

       ``<robot>_wmx_parameters.xml``
     - Gear ratios, encoder resolution, polarity, homing, and limits, per WMX
       axis index.
   * - **URDF / xacro**

       ``<robot>.xacro``, ``.ros2_control.xacro``, ``.srdf``
     - Link geometry, joint axes and origins, planning limits, and the
       ``ros2_control`` hardware interface.
   * - **ROS 2 parameter YAML**

       application, controller, MoveIt, Nav2, and perception YAML
     - Joint-name ↔ axis-index mapping, I/O addresses, and the planner and
       controller settings.

:doc:`robot_parameters` lists exactly where each of these lives and what goes
in it. The stages below are how you verify that what you put in them is
right — that work, not a code change, is what commissioning a new machine
actually costs.

.. _simulation-first-workflow:

The simulation-first workflow
-----------------------------

Every stage below exists to catch a class of error while it is still cheap.
Do not skip stages, and do not run a later stage until the previous one is
clean.

.. list-table::
   :header-rows: 1
   :widths: 6 26 40 28

   * - #
     - Stage
     - What it proves
     - What it catches
   * - 0
     - **Network and engine setup in the UI**

       (:doc:`wmx_web_tools`)
     - The bus is described and the engine is reachable: every slave is
       recognised, the ENI file is generated, and the axis parameters are
       loaded into the engine and read back.
     - Missing ESI files, a stale or absent ENI, slaves that never reach
       ``Op``, and parameters left behind by a previous session.
   * - 1
     - **Parameter configuration and review**

       (:doc:`robot_parameters`)
     - The joint↔axis map, gear ratios, encoder resolution, directions, home
       offsets, and limits are written down and cross-checked against the
       URDF, the MoveIt configuration, and the WMX parameter file.
     - Typos, copied-from-another-robot values, and URDF/WMX disagreement.
   * - 2
     - **Simulation**

       (Isaac Sim or Gazebo, no WMX runtime)
     - The kinematics, planning scene, joint limits, and application logic are
       correct.
     - Bad URDF, unreachable targets, planner and collision errors.
   * - 3
     - **HIL**

       (simulator visuals, real WMX runtime, simulated bus)
     - The real WMX engine loads your parameter file, accepts the planner's
       trajectories, and produces the motion you expect — with no drive
       powered.
     - Parameter-file load failures, unit and scaling mistakes, trajectory
       rejections, engine and timing problems.
   * - 4
     - **Low-speed single-axis jogging**

       (:doc:`first_motion`)
     - Each physical axis is the joint you think it is, moves in the direction
       you think it does, travels the distance you command, and reports
       feedback that agrees.
     - Swapped axes, inverted polarity, wrong gear ratio, wrong home offset.
   * - 5
     - **Multi-axis motion on physical hardware**
     - Coordinated motion stays inside the workspace and clear of the robot's
       own structure and its surroundings.
     - Collisions and limit violations that a single axis cannot reveal.
   * - 6
     - **Trajectory execution**
     - Planner output executes end to end at working speed.
     - Timing, blending, and tracking-error problems.

.. note::

   Stage 0 is done in the browser tools, not in ROS 2, and is the only stage
   that needs no WMX R2 package built. Stages 2 and 3 map directly onto the
   **Simulation** and **HIL** tabs used throughout
   :doc:`../examples/examples`. Stage 6 is the **Real** tab. Stages 4 and 5
   sit between them and are described in :doc:`first_motion`.

Where the stages are documented
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Page
     - Covers
   * - :doc:`wmx_web_tools`
     - **Start here.** The browser tools shipped with the WMX Runtime — the UI
       you use to generate the EtherCAT ENI file, set and export axis
       parameters, and jog an axis to test it, all without ROS 2 in the way.
   * - :doc:`robot_parameters`
     - Every robot-specific parameter, where it lives, what it means, where
       its value comes from, and how to verify it against the running engine.
   * - :doc:`first_motion`
     - The first-motion procedure: single axis, low speed,
       what to check at each step, and the exact stopping behavior of the jog
       tools.
   * - :doc:`safety`
     - Which safety functions are *not* provided when the original robot
       controller is bypassed, and the separate measures a physical system
       requires.
   * - :doc:`validated_hardware`
     - Which robots have been validated on physical hardware, which functions
       were tested, and what is untested or experimental.

.. toctree::
   :maxdepth: 2
   :hidden:

   wmx_web_tools
   robot_parameters
   first_motion
   safety
   validated_hardware
