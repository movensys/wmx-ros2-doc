Natural-Language and Vision Control (VLM / LLM)
===============================================

`Movensys Intelligence <https://github.com/movensys/movensys-intelligence>`_
is an application layer on top of WMX R2 that lets a robot be driven by
natural language and vision. A vision-language model (VLM) and large language
model (LLM) interpret camera images and spoken or typed instructions, then
issue motion commands to the robot through a FastAPI service that bridges to
the WMX R2 / MoveIt2 stack.

Unlike the other entries in this section, this is **not** a motion-planning
backend. It runs above a planning backend (MoveIt2) and calls the
``/wmx/moveit2/*`` services to move the arm.

Architecture
------------

.. mermaid::
   :caption: Movensys Intelligence — perception and language to motion
   :zoom:

   flowchart LR
       USER["Voice / text<br/>instruction"]
       WHISPER["Whisper STT"]
       VLM["VLM / LLM<br/>(vLLM, OpenAI API)"]
       MEM["Memory<br/>(Qdrant vector DB)"]
       API["FastAPI service<br/>Movensys Manipulator API"]
       BRIDGE["ROS2 bridge node"]
       WMX["WMX R2 / MoveIt2"]
       ROBOT["Robot + cameras"]
       YOLO["YOLO detectors"]

       USER --> WHISPER --> API
       USER --> API
       API --> VLM
       VLM <--> MEM
       VLM --> API
       API --> BRIDGE --> WMX --> ROBOT
       ROBOT --> YOLO --> BRIDGE
       BRIDGE --> API

The flow is: a spoken instruction is transcribed by **Whisper**, or text is
sent directly. The **VLM/LLM** receives the instruction together with the
latest camera images and any relevant context retrieved from the **memory**
store, and produces a motion command. The **FastAPI** service forwards that
command through its **ROS2 bridge** to the WMX R2 / MoveIt2 services, which
execute the motion on the robot. Perception nodes (**YOLO** detectors) publish
detected object poses back through the bridge.

Components
----------

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Component
     - Role
   * - **FastAPI service** (``movensys_vlm/main.py``)
     - "Movensys Manipulator API" — hosts the REST + WebSocket API, web UI,
       and the ROS2 bridge node
   * - **vLLM**
     - Serves the VLM/LLM behind an OpenAI-compatible endpoint
       (``VLM_BASE_URL``, default ``http://localhost:9000/v1``;
       ``VLM_MODEL_NAME`` selects the model)
   * - **Whisper**
     - Speech-to-text for voice instructions
       (``POST /api/whisper/transcribe``)
   * - **Qdrant vector DB**
     - Long-term memory / retrieval for the language model
       (``MEMORY_*`` settings)
   * - **Arize Phoenix** (optional)
     - Tracing and observability for model calls (``PHOENIX_*`` settings)
   * - **ROS2 bridge** (``movensys_vlm/ros2_node.py``)
     - Subscribes to robot state, camera, and perception topics and calls the
       WMX R2 / MoveIt2 motion services

Connection to WMX R2
----------------------

The ROS2 bridge node talks to the WMX R2 / MoveIt2 stack through these
interfaces:

.. list-table::
   :header-rows: 1
   :widths: 45 25 30

   * - Interface
     - Direction
     - Purpose
   * - ``/wmx/moveit2/get_eef_pose``
     - service client
     - Read the current end-effector pose
   * - ``/wmx/moveit2/absolute_base_eef_cartesian``
     - service client
     - Move to an absolute Cartesian pose (base frame)
   * - ``/wmx/moveit2/relative_base_eef_cartesian``
     - service client
     - Move by a relative Cartesian offset (base frame)
   * - ``/wmx/moveit2/relative_tool_eef_cartesian``
     - service client
     - Move by a relative Cartesian offset (tool frame)
   * - ``/wmx/moveit2/{absolute_base_eef_joint_movement, joint_movement, relative_joint_movement}``
     - service client
     - Joint-space moves
   * - ``/wmx/set_gripper``
     - service client
     - Open/close the gripper (``std_srvs/srv/SetBool``)
   * - ``/joint_states``
     - subscribe
     - Joint feedback for the live UI
   * - ``/image_top/*`` and ``/image_hand/*``
     - subscribe
     - RGB, depth, and camera info for the VLM and UI
   * - ``/piece_1``, ``/piece_2``, ``/dice``, ``/yolo_*``
     - subscribe
     - Detected object poses from the YOLO detectors

The custom service types (``GetEefPose``, ``MovePose``, ``MoveJoints``) come
from the ``movensys_manipulator_moveit_config`` package.

API Surface
-----------

The FastAPI service exposes (among others):

- **Language** — ``POST /api/vlm/infer``, ``GET /api/vlm/system_prompt``,
  ``GET /api/vlm/memory``, ``POST /api/whisper/transcribe``
- **Motion** — ``POST /api/move/absolute_cartesian_base``,
  ``/api/move/relative_cartesian_base``, ``/api/move/relative_cartesian_tool``,
  ``/api/move/joint_absolute``, ``/api/move/joint_relative``,
  ``POST /api/services/gripper``
- **State streams** — WebSocket endpoints under ``/api/stream/*`` for
  end-effector pose, joint states, and camera feeds
- **Web UI** — ``/cameras`` and ``/vlm`` pages, with OpenAPI docs at ``/docs``

Running It
----------

Movensys Intelligence runs as a set of Docker Compose services.

.. list-table:: Services and ports
   :header-rows: 1
   :widths: 26 12 62

   * - Service
     - Port
     - Purpose
   * - ``movensys_vlm``
     - 8000
     - FastAPI REST/WebSocket API and the ROS2 bridge
   * - ``vllm``
     - 9000
     - OpenAI-compatible inference server
   * - ``whisper``
     - 9010
     - Speech-to-text
   * - ``vectordb`` (Qdrant)
     - 6333
     - Long-term vector memory
   * - ``movensys_robopoly``
     - 7999
     - The Robopoly sample application
   * - ``phoenix`` (optional)
     - 6006
     - LLM trace UI

.. important::

   Local model weights must already be under ``movensys_vlm/models/`` —
   Gemma 4 E2B/E4B, Whisper large-v3, and the embedding model. Nothing is
   downloaded for you.

Set the accelerator and architecture, then bring the stack up **in this
order** — each service depends on the one before it:

.. code-block:: bash

   export XPU_CORE=nvidia-gpu        # {nvidia-gpu, intel-xpu}
   export CPU_ARCH=amd64             # {amd64, arm64}

   cd ~/workspaces/movensys-intelligence/movensys_vlm/docker

   # 1. Serve the VLM/LLM with vLLM
   COMPOSE_PROFILES=$XPU_CORE docker compose -f vllm.yaml up -d --build

   # 2. Vector-DB memory (profile is CPU_ARCH, not XPU_CORE)
   COMPOSE_PROFILES=$CPU_ARCH docker compose -f vectordb.yaml up -d --build

   # 3. Speech-to-text
   COMPOSE_PROFILES=$XPU_CORE docker compose -f whisper.yaml up -d --build

   # 4. The FastAPI service and ROS2 bridge
   COMPOSE_PROFILES=$XPU_CORE docker compose -f movensys_vlm.yaml up -d --build

Intel Panther Lake builds vLLM on a separate path:

.. code-block:: bash

   cd ~/workspaces/movensys-intelligence/movensys_vlm/docker
   ./vllm-intel-build.sh
   ./vllm-intel-run.sh

Wait until the vLLM container logs ``application startup complete`` before
sending requests. A pick-and-place example is included in the repository:

.. code-block:: bash

   cd ~/workspaces/movensys-intelligence
   python3 movensys_sample/movensys_robopoly/pick_and_place.py red_cube GO true

.. note::

   The Movensys Intelligence services connect to a running WMX R2 /
   MoveIt2 session. Bring up the robot (or simulation) first — see
   :doc:`moveit2_integration` and
   :doc:`../getting_started/install_wmx3`.

Supported accelerators include NVIDIA desktop GPUs and Jetson Thor
(``nvidia-gpu``) and Intel B60 / Panther Lake (``intel-xpu``).

.. tip::

   On Jetson Thor or Intel Panther Lake, drop kernel caches between restarts
   if memory pressure builds up: ``sync && sudo sysctl vm.drop_caches=3``

The full bring-up, teardown, and Phoenix-tracing options are in
``movensys_vlm/doc/running.md``. See :doc:`../examples/robopoly_game` for the
sample application end to end.
