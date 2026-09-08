WMX R2 Documentation
=======================

**WMX R2: The Real-Time Execution Layer for Physical AI.**

WMX R2 brings industrial deterministic real-time robotics motion control into the
ROS 2 ecosystem. WMX R2 is a solution that integrates a ROS 2 interface with
the WMX motion engine. It drives industrial servos over EtherCAT, a
real-time industrial Ethernet network that links the controller to servo drives
and I/O over a single cable.

WMX R2 turns planner output such as MoveIt2 and Nav2 trajectories into the precisely timed
servo motion that industrial and Physical AI applications demand.
In the *See–Think–Act* flow of Physical AI, WMX R2 is the layer that turns an
AI's judgment (*Think*) into a robot's real-world motion (*Act*), in real time. 

.. figure:: /_static/images/wmx-r2_pai.png
   :alt: WMX R2 for physical AI
   :align: center
   :width: 100%

The entire stack runs on a single edge device with no separate external motion
controller, combining perception and deterministic motion into edge physical AI.

**WMX R2 runs on any robot or machine that uses EtherCAT.**

WMX R2 integrates with widely used projects in the ROS2 ecosystem:

* `MoveIt2 <https://moveit.ai/>`_ for manipulator motion planning
* `Nav2 <https://nav2.org/>`_ for mobile robot navigation
* `ros2_control <https://control.ros.org/>`_ for hardware interface and controller management
* `Intel OpenVINO <https://docs.openvino.ai/2026/index.html>`_ for optimized inference on
  Intel XPU and integrated accelerators
* `NVIDIA Isaac Sim <https://developer.nvidia.com/isaac/sim>`_ and
  `Gazebo <https://gazebosim.org/>`_ for simulation
* `NVIDIA Isaac ROS <https://developer.nvidia.com/isaac/ros>`_ for NVIDIA GPU
  accelerated perception and control
* `YOLO <https://docs.ultralytics.com/>`_ for real time object detection
* Multimodal large language models (LLMs) and vision language models
  (VLMs) for natural language task specification and high level reasoning

See WMX R2 in action:

.. raw:: html

   <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
     <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
             src="https://www.youtube-nocookie.com/embed/2JlqxwyMN_E"
             title="WMX R2 demo video for Intel Edge Day"
             allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
             allowfullscreen></iframe>
   </div>


.. raw:: html

   <div style="position: relative; width: 100%; max-width: 800px; margin: 1em auto; aspect-ratio: 16 / 9;">
     <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;"
             src="https://www.youtube-nocookie.com/embed/h-G9vtAGAIU"
             title="WMX R2 demo video for GTC conference"
             allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
             allowfullscreen></iframe>
   </div>

To show how these pieces fit together, four companion repositories are provided
as working examples and reference implementations built on WMX R2:

.. mermaid::
   :caption: The five repositories and what each one owns

   flowchart TB
       INT["<b>movensys-intelligence</b><br/>VLM · Whisper · Robopoly<br/><i>speaks and reasons</i>"]

       subgraph APP["Application layer"]
           direction LR
           MAN["<b>movensys-manipulator</b><br/>MoveIt2 · cuMotion<br/>Nvblox · YOLO · AprilTag<br/><i>plans arm motion</i>"]
           NAV["<b>movensys-navigation</b><br/>Nav2 · EKF · SLAM<br/><i>plans base motion</i>"]
       end

       SIM["<b>movensys-simulation</b><br/>Isaac Sim USD scenes<br/><i>the digital twin</i>"]

       WMX["<b>wmx-r2</b><br/>ROS2 interface + WMX engine<br/><i>executes, in real time</i>"]
       HW["Servo drives and I/O<br/>over EtherCAT"]

       INT -->|"/wmx/moveit2/* services"| MAN
       MAN -->|"FollowJointTrajectory"| WMX
       NAV -->|"/cmd_vel_safe"| WMX
       WMX --> HW
       HW -->|"encoder"| WMX
       WMX -->|"/joint_states, /odom_enc"| APP
       SIM -.->|"scenes for Simulation and HIL"| APP
       WMX -.->|"mirror topics"| SIM

* `movensys-manipulator <https://github.com/movensys/movensys-manipulator>`_ :
  manipulator scenarios with MoveIt2 / Isaac cuMotion
  planning and Nvblox / YOLO / AprilTag perception
* `movensys-navigation <https://github.com/movensys/movensys-navigation>`_ :
  a differential-drive mobile base with Nav2 planning, EKF odometry, and SLAM mapping
* `movensys-intelligence <https://github.com/movensys/movensys-intelligence>`_ :
  a voice-driven VLM/LLM application (the Robopoly game) built on top of the
  manipulator stack
* `movensys-simulation <https://github.com/movensys/movensys-simulation>`_ :
  the Isaac Sim scenes used by the manipulator and navigation scenarios

Each application repository runs in its own container and talks to WMX R2 over
DDS, so the planning stack and the real-time stack stay separate processes on
the same machine.

See :doc:`examples/examples` to run these scenarios from start to finish.



.. figure:: /_static/images/wmx-r2_overview.drawio.png
   :alt: WMX R2 architecture overview
   :align: center
   :width: 100%

   WMX R2 architecture overview.

Any EtherCAT system, any robot
----------------------------------------

**WMX R2 runs on any robot or machine that uses EtherCAT.**

WMX R2 sends commands to servo drives over EtherCAT using standard CoE. It does
not go through the robot manufacturer's controller, so it does not depend on the
brand of the robot or of the drives. It controls axes rather than a specific
robot model, so a six-axis arm, a differential-drive mobile base, and a custom
multi-axis machine are all driven the same way.

Moving to a different robot means changing three files: the axis parameter file,
the URDF, and the planning configuration. The motion engine, the ROS 2
interface, and the real-time cycle stay the same.

WMX R2 also provides general nodes for axis, I/O, engine, and EtherCAT control.
You can use them to read and command any EtherCAT device on the network before
writing a configuration for a specific robot.

Why WMX R2?
----------------------------------------

A planner such as MoveIt2 or Nav2 produces a trajectory that must become the
precisely timed signals servo drivers execute on a fixed cycle. Most
ROS2 setups bridge this execution gap with a closed industrial
controller over TCP/IP, which adds latency the planner can never
recover. The other common option sends raw EtherCAT commands and leaves
smoothing and coordination to ROS2, which is not built for hard
real-time system. WMX R2 closes this gap by bringing the WMX motion control engine into ROS2
so planner output runs as smooth deterministic motion in one single edge device.

.. figure:: /_static/images/one_ipc.png
   :alt: Conventional motion control versus WMX software motion on a single PC
   :align: center
   :width: 100%

   Conventional motion control routes the PC through a separate dedicated
   motion controller; WMX software motion drives the servo drives directly
   from a single edge device over the field network.

Moving the controller into the PC removes an enclosure and its cabling, so
the system is smaller, lighter, and efficient while performing better. That
compact footprint suits robots and mobile machines where space and payload are
tight.


WMX R2's ROS 2 interface handles the timing-sensitive step: smoothing
trajectories, coordinating joints, and emitting commands at the rate servo
drivers expect. Its source code is open source under the MIT license. It runs
with the WMX motion engine, which keeps motion on a deterministic cycle and
exposes more than 200 APIs for trajectory conversion, EtherCAT, I/O, and engine
control. The engine, its SDK, and its binaries are proprietary and require an
evaluation or commercial license: the engine runs free in renewable 6-hour
sessions that you extend by restarting it, and a commercial license removes the
limit for production.

Performance comparison
~~~~~~~~~~~~~~~~~~~~~~~

.. grid:: 1 1 2 2
   :gutter: 3

   .. grid-item::

      .. figure:: /_static/images/graph_1.png
         :alt: Representative single run — joint-angle tracking
         :width: 100%

         Representative run: joint-angle tracking for the reference, the
         traditional external controller, and the proposed WMX R2.

   .. grid-item::

      .. figure:: /_static/images/graph_2.png
         :alt: Mean absolute tracking error across ten runs
         :width: 100%

         Per-sample mean absolute error across ten runs.

We executed the same trajectory ten times. The left panel shows a representative run,
and the right panel presents the per-sample mean absolute tracking error (MAE).
The overall MAE corresponds to the time average of this curve. WMX R2 reduced
the MAE by 85% relative to the conventional external controller, thanks to lower
communication latency from removing the TCP/IP hop and a redundant control stage.

Customers and Partners
----------------------------------------

The WMX motion engine has a long, proven industrial track record:

* 25+ years of development with 40+ patents worldwide
* 40,000+ cumulative licenses sold
* 500+ customers, mainly in the semiconductor industry

.. Add customer and partner logos or names here.

Where to go next
----------------------------------------

* Follow the :doc:`getting_started/index` guide to set up the environment and run the package.
* Work through the :doc:`examples/examples` to run trajectory, perception, and intelligence demos.
* See :doc:`integration/integration` for the supported motion-planning and application integrations.
* Work through :doc:`commissioning/index` before moving a physical robot;
  parameter validation, first motion, safety responsibilities, and the list of
  validated robots.
* Refer to the :doc:`api_reference/api_reference` for ROS2 services, topics, and actions.
* Consult :doc:`support` for common issues and their resolutions.
* Read :doc:`licensing` for the boundary between the MIT-licensed ROS 2
  interface and the proprietary WMX motion engine.








.. toctree::
   :maxdepth: 3

   getting_started/index
   examples/examples
   integration/integration
   commissioning/index
   api_reference/api_reference
   support
   licensing
   about