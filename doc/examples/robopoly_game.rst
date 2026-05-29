Robopoly Game (VLM / LLM)
=========================

Robopoly is a voice-driven, vision-language pick-and-place game from the
`movensys-intelligence <https://github.com/movensys/movensys-intelligence>`_
repository (``movensys_sample/movensys_robopoly``). You speak game actions and
the robot executes them, using YOLO object detection and the VLM/LLM service
to interpret instructions and game state. It is built on top of the
manipulator stack and the VLM service described in
:doc:`../integration/intelligence_integration`.

Components
----------

- **movensys_robopoly** -- the game application and web UI
  (``movensys_sample/movensys_robopoly``)
- **VLM service** (``movensys_vlm``) -- vision-language model, Whisper
  speech-to-text, and memory (see ``movensys_vlm/doc/running.md``)
- **Manipulator stack** -- the YOLO scenario from
  :doc:`yolo_pick_and_place` provides perception and motion

Running in Dry-Run Mode
-----------------------

Dry-run needs no robot or simulator; it exercises the game logic and UI only.

.. code-block:: bash

   export MOVENSYS_PNP_DRY_RUN=1
   cd ~/workspaces/movensys-intelligence/movensys_sample/movensys_robopoly/docker
   docker compose down
   docker compose build
   docker compose up -d

Then in the web UI: toggle ``is_YOLO`` **OFF**, select your microphone, click
**Reset game**, and use the voice controls below.

Running with Simulation
-----------------------

1. Start the manipulator stack and the YOLO simulation scenario -- follow
   ``movensys-manipulator/doc`` steps ``1_`` and ``2_``, then
   ``6a_yolo_simulation.md`` (see :doc:`yolo_pick_and_place`).
2. Start the VLM service -- follow ``movensys_vlm/doc/running.md``.
3. Start Robopoly with the robot loop enabled:

   .. code-block:: bash

      export MOVENSYS_PNP_DRY_RUN=0
      cd ~/workspaces/movensys-intelligence/movensys_sample/movensys_robopoly/docker
      docker compose down
      docker compose build
      docker compose up -d

4. In the web UI: toggle ``is_YOLO`` **ON**, click **Reset game**, and play.

Running on the Real Robot
-------------------------

A helper script, ``movensys_sample/doc/run_robopoly.sh``, orchestrates the
required services across terminals:

.. code-block:: bash

   cd ~/workspaces/movensys-intelligence/movensys_sample/doc

   # Terminal 1: launch WMX ROS2
   ./run_robopoly.sh wmx-ros2

   # Terminal 2: build the containers for your accelerator
   ./run_robopoly.sh build_nvidia     # or: ./run_robopoly.sh build_intel

   # Terminal 3: run MoveIt2, the containers, and YOLO
   ./run_robopoly.sh run

Voice Controls
--------------

- **Z key** -- hold and speak to request a game action
- **X key** -- hold and speak to communicate game status or strategy
- **Toggle is_YOLO** -- enable (ON) detection-driven play, or disable (OFF) for
  dry-run
- **Reset game** -- start a new game

Debug Tips
----------

.. code-block:: bash

   docker logs -f vllm_container          # VLM/LLM server
   docker logs -f movensys-manipulator    # manipulator container
   tmux a -t robopoly                     # MoveIt2 / launch logs

An automated dry-run test is also available:

.. code-block:: bash

   cd ~/workspaces/movensys-intelligence/movensys_sample/movensys_robopoly/
   python3 scripts/auto_play_dry_run.py

See :doc:`../integration/intelligence_integration` for the VLM/LLM service
architecture and API.
