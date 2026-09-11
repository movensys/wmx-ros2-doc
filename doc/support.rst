Support
=======

This section provides solutions to common issues encountered when setting up
and running the WMX R2 application.

The **Troubleshooting** guide covers the most frequent problems organized by
category: WMX device creation failures, EtherCAT network scan issues,
communication startup errors, joint state problems, servo alarm codes,
trajectory execution failures, gripper control issues, missing ROS2 nodes,
and build errors. Each problem includes symptoms, likely causes, and
step-by-step solutions.

.. note::

   Unexpected motion on a physical robot: wrong direction, wrong distance,
   wrong joint, or a constant offset is almost always a robot-parameter
   problem rather than a software fault. Start at
   :doc:`try_your_robot/robot_parameters`, and see
   :doc:`try_your_robot/validated_hardware` for what has been validated on your
   robot and what has not.

For additional help, contact your MOVENSYS representative or visit
`movensys.com <https://www.movensys.com/en/>`_.

**Documentation issues:** to report an error or a gap in this documentation,
open an issue on `GitHub Issues
<https://github.com/movensys/wmx-r2-doc/issues>`_.

.. toctree::
   :maxdepth: 2

   troubleshooting/troubleshooting
