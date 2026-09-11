Robopoly Game (VLM / LLM)
=========================

Robopoly is a voice-driven, vision-language pick-and-place game from the
`movensys-intelligence <https://github.com/movensys/movensys-intelligence>`_
repository (``movensys_sample/movensys_robopoly``). You speak a game action,
a vision-language model decides what to do, and the arm plays the move.

It is the top of the whole stack: speech in, VLM reasoning, YOLO perception,
MoveIt2 planning, and WMX R2 executing the motion on the servos.

.. mermaid::
   :caption: Robopoly, from voice to servo

   flowchart LR
       MIC["Microphone<br/>(Z / X key)"]
       WH["whisper<br/>:9010"]
       VLM["movensys_vlm<br/>:8000<br/>(FastAPI + ROS2 bridge)"]
       LLM["vllm<br/>:9000<br/>Gemma"]
       DB["Qdrant<br/>:6333"]
       RP["movensys_robopoly<br/>:7999<br/>game rules + UI"]
       YOLO["YOLO dice &amp; cube<br/>detector"]
       MI["moveit2_api<br/>/wmx/moveit2/*"]
       WMX["WMX R2<br/>joint_trajectory_controller"]
       ARM["Arm + gripper<br/>(EtherCAT)"]

       MIC --> WH --> VLM
       VLM <--> LLM
       VLM <--> DB
       VLM <--> RP
       YOLO --> RP
       RP --> MI --> WMX --> ARM

Components
----------

.. list-table::
   :header-rows: 1
   :widths: 26 12 62

   * - Service
     - Port
     - Role
   * - ``movensys_robopoly``
     - 7999
     - Game rules, board state, and the web UI you play in
   * - ``movensys_vlm``
     - 8000
     - FastAPI VLM service plus the ROS2 bridge that calls
       ``/wmx/moveit2/*``
   * - ``vllm``
     - 9000
     - OpenAI-compatible inference server hosting the Gemma model
   * - ``whisper``
     - 9010
     - Streaming speech-to-text
   * - ``vectordb`` (Qdrant)
     - 6333
     - Long-term vector memory for the agent
   * - ``phoenix`` (optional)
     - 6006
     - OpenTelemetry / LLM trace UI

Underneath, the manipulator stack supplies perception and motion — the YOLO
dice-and-cube detector and the MoveIt2 service API — and WMX R2 executes the
trajectories. See :doc:`yolo_pick_and_place` and
:doc:`../integration/intelligence_integration`.

Host environment
----------------

In addition to the ``movensys-manipulator`` variables
(:doc:`movensys_manipulator_setup`), add:

.. code-block:: bash

   export XPU_CORE=nvidia-gpu        # {nvidia-gpu, intel-xpu}
   export CPU_ARCH=amd64             # {amd64, arm64}

.. important::

   Robopoly runs the manipulator container on the ``general`` build flavor,
   not an ``isaac-ros`` one:

   .. code-block:: bash

      export MOVENSYS_ROS_VERSION=general

   Local model weights must be present under ``movensys_vlm/models/`` —
   Gemma 4 E2B/E4B, Whisper large-v3, and the embedding model. They are not
   downloaded automatically.

Clone the repository into ``~/workspaces`` (**not** into ``movensys_ws/src``
— it is not a ROS package):

.. code-block:: bash

   mkdir -p ~/workspaces
   cd ~/workspaces
   git clone https://github.com/movensys/movensys-intelligence.git

Dry run — no robot, no simulator
--------------------------------

The fastest way to see the stack work. It exercises speech, the VLM, and the
game logic, and skips arm motion entirely.

.. code-block:: bash

   export MOVENSYS_PNP_DRY_RUN=1
   cd ~/workspaces/movensys-intelligence/movensys_sample/movensys_robopoly/docker
   docker compose down
   docker compose build
   docker compose up -d

Open ``http://localhost:7999/``, then:

1. Toggle ``is_YOLO`` **OFF**.
2. Select your microphone.
3. Click **Reset game**.
4. Hold **Z** and speak a game action; hold **X** and speak about game status
   or strategy.

An automated dry-run test is also available:

.. code-block:: bash

   cd ~/workspaces/movensys-intelligence/movensys_sample/movensys_robopoly/
   python3 scripts/auto_play_dry_run.py

Simulation
----------

1. Set up ``movensys-manipulator`` (:doc:`movensys_manipulator_setup`) with
   ``MOVENSYS_ROS_VERSION=general``.

2. Open ``~/workspaces/movensys-simulation/<MANIPULATOR_MODEL>/7a_robopoly_simulation.usd``
   in Isaac Sim and press **Play**. Robopoly has its own scene — it carries
   the board, dice, and tray assets.

3. Build the containers:

   .. code-block:: bash

      cd ~/workspaces/movensys-intelligence/movensys_sample/doc
      ./run_robopoly.sh build_nvidia

4. Run the simulator bridge:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config sim_bridge.launch.py \
           simulator:=isaacsim use_sim_time:=true

5. Launch MoveIt2 OMPL and the service API:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_moveit_config moveit.launch.py \
           use_sim_time:=true

6. Launch the YOLO dice-and-cube detector:

   .. code-block:: bash

      mros ros2 launch movensys_manipulator_perception \
           yolo_dice_and_cube_detector.launch.py use_sim_time:=true

7. In the web UI, toggle ``is_YOLO`` **ON**, click **Reset game**, and play.

Real robot
----------

.. danger:: **This moves a physical arm under model control.**

   The VLM decides the moves. Complete :doc:`../try_your_robot/index` first,
   keep the workspace clear, and keep a hand on the emergency stop.

``movensys_sample/doc/run_robopoly.sh`` orchestrates the services across
three terminals.

.. tab-set::

   .. tab-item:: NVIDIA (desktop GPU / Jetson Thor)

      .. code-block:: bash

         cd ~/workspaces/movensys-intelligence/movensys_sample/doc

         # Terminal 1: launch WMX R2 (prompts for sudo, stays in foreground)
         ./run_robopoly.sh wmx-r2

         # Terminal 2: build images and start the persistent containers
         ./run_robopoly.sh build_nvidia

         # Terminal 3: run MoveIt2, the containers, and YOLO in a tmux session
         ./run_robopoly.sh run

   .. tab-item:: Intel XPU (B60 / Panther Lake)

      .. code-block:: bash

         cd ~/workspaces/movensys-intelligence/movensys_sample/doc

         # Terminal 1: launch WMX R2
         ./run_robopoly.sh wmx-r2

         # Terminal 2: build and start vLLM on its own path
         ./run_robopoly.sh build_intel_vllm

         # Terminal 3: build the remaining services
         ./run_robopoly.sh build_intel

         # Terminal 3: run MoveIt2, the containers, and YOLO
         ./run_robopoly.sh run

Wait for the build to finish before running:

.. code-block:: bash

   docker logs -f movensys_manipulator_container

.. note::

   ``run_robopoly.sh`` takes ``MOVENSYS_MANIPULATOR_PACKAGES``,
   ``MOVENSYS_ROS_VERSION``, ``CPU_ARCH``, ``XPU_CORE``, and
   ``MANIPULATOR_MODEL`` from the environment, and falls back to the standard
   ``~/workspaces`` layout with ``dobot_cr3a`` when they are unset. Override
   any of them if your layout differs:

   .. code-block:: bash

      export MOVENSYS_MANIPULATOR_PACKAGES=~/workspaces/movensys_ws/src/movensys-manipulator

   ``MANIPULATOR_MODEL`` also selects which WMX R2 example files the driver
   launches — ``dobot_cr3a`` uses ``cr3a_manipulator_config.yaml`` and
   ``cr3a_wmx_parameters.xml``. The gripper is enabled
   (``use_gripper:=true``); Robopoly cannot pick without it.

Voice controls
--------------

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Control
     - Action
   * - **Z** (hold)
     - Speak a game action — "roll the dice", "move my piece to Go"
   * - **X** (hold)
     - Speak about game status or strategy
   * - ``is_YOLO`` toggle
     - **ON** for detection-driven play, **OFF** for dry run
   * - **Reset game**
     - Start a new game

Pick-and-place from the command line
------------------------------------

Bypass the game and time a single pick-and-place:

.. code-block:: bash

   cd ~/workspaces/movensys-intelligence
   python3 movensys_sample/movensys_robopoly/pick_and_place.py red_cube GO true 2>&1 | tee baseline.log
   grep '\[timing\]' baseline.log

Debugging
---------

.. code-block:: bash

   docker logs -f vllm_container                 # inference server
   docker logs -f movensys_manipulator_container  # manipulator container
   tmux a -t robopoly                             # MoveIt2 and YOLO logs

Inside ``tmux``: ``Ctrl-b`` then ``d`` detaches, ``Ctrl-b`` then a window
number switches windows, and ``Ctrl-b`` then ``[`` enters scroll mode
(``PgUp`` / ``PgDn`` to scroll).

.. tip::

   On Jetson Thor or Intel Panther Lake, drop kernel caches between restarts
   if memory pressure builds up:

   .. code-block:: bash

      sync && sudo sysctl vm.drop_caches=3

See :doc:`../integration/intelligence_integration` for the VLM service
architecture and API, and ``movensys_vlm/doc/running.md`` for the full
bring-up and teardown sequence.

.. toctree::
   :maxdepth: 1

   robopoly_detailed_guide
