movensys-manipulator
====================

The manipulator scenarios come from the
`movensys-manipulator <https://github.com/movensys/movensys-manipulator>`_
repository: manipulator with MoveIt2 / Isaac cuMotion planning and
Nvblox / YOLO / AprilTag perception. Each scenario runs in Simulation, HIL, and
Real modes.

Set up the stack once with :doc:`movensys_manipulator_setup` before running any
scenario. The **Robopoly game** is a voice-driven VLM/LLM application from the
`movensys-intelligence <https://github.com/movensys/movensys-intelligence>`_
repository, built on top of this manipulator stack.

.. toctree::
   :maxdepth: 1

   movensys_manipulator_setup
   trajectory_planning
   apriltag_pick_and_place
   obstacle_avoidance
   yolo_pick_and_place
   apriltag_obstacle_avoidance
   robopoly_game
