Getting Started
===============

This guide walks you through the complete setup — from system requirements to
launching your first robot control session with WMX R2.

Follow the steps in order. At step 6 choose the path that matches your setup
(simulation or physical robot).

.. figure:: /_static/images/getting_started.drawio.png
   :alt: Getting Started — step-by-step flow 
   :align: center

   Getting Started — step-by-step flow

.. warning:: **This guide stops at "the software runs".**

   Completing these steps means the WMX runtime, the ROS 2 packages, and the
   EtherCAT bus are working. It does **not** mean the robot will move the way
   you intend. The gear ratios, encoder resolution, joint directions, and home
   offsets that decide the actual motion still have to be configured and
   verified, and the safety functions of the robot manufacturer's original
   controller are not available once that controller is bypassed.

   Before commanding motion on a physical robot, continue with
   :doc:`../try_your_robot/index`.

.. toctree::
   :maxdepth: 1
   :hidden:

   computer_setup
   install_wmx_runtime
   install_wmx3