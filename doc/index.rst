WMX ROS2 Documentation
=======================

Welcome to the WMX ROS2 documentation. This project provides ROS2
packages for controlling robot platforms through the WMX motion control
engine over EtherCAT. It targets industrial applications that require
deterministic and high precision motion, such as semiconductor
equipment, manufacturing automation, and precision robotics. The entire
stack runs on a single industrial PC (IPC) or edge device with no
separate motion controller. A Real-Time OS is required
so that motion timing stays predictable under load.

WMX ROS2 integrates with widely used projects in the ROS2 ecosystem:

* `MoveIt2 <https://moveit.ai/>`_ for manipulator motion planning
* `NVIDIA Isaac Sim <https://developer.nvidia.com/isaac/sim>`_ and
  `Gazebo <https://gazebosim.org/>`_ for simulation
* `NVIDIA Isaac ROS <https://developer.nvidia.com/isaac/ros>`_ for GPU
  accelerated perception
* `YOLO <https://docs.ultralytics.com/>`_ for real time object detection
* `Intel OpenVINO <https://docs.openvino.ai/2026/index.html>`_ for optimized inference on
  CPU and integrated accelerators
* Multimodal large language models (LLMs) and vision language models
  (VLMs) for natural language task specification and high level reasoning



.. figure:: /_static/images/wmx-ros2_overview.drawio.png
   :alt: WMX ROS2 architecture overview
   :align: center
   :width: 100%

   WMX ROS2 architecture overview.

Why need a Real-Time OS?
----------------------------------------

Servo drivers expect a command every fixed cycle. Standard Linux
optimizes for throughput rather than keeping a strict deterministic
schedule, so it may pause the program for a few milliseconds to handle
a packet or a background task. That delay makes the next command arrive
late and miss its cycle. A missed cycle makes motion stutter and drops
accuracy, and on a production line it can even fault the drivers and
stop the machine. A Real-Time OS such as Linux with the PREEMPT_RT
patch guarantees motion threads run on time even under load, which is
why every industrial motion stack runs on one.

Why WMX ROS2?
----------------------------------------

A Real-Time OS covers the kernel-level guarantees, but ROS2 still
leaves one step uncovered. A planner such as MoveIt2 or Nav2 produces a
trajectory and `ros2_control <https://control.ros.org/>`_ sends joint
commands to the hardware. Those commands still need to become the
precisely timed signals servo drivers execute on a fixed cycle. Most
ROS2 setups bridge this execution gap with a closed industrial
controller over TCP/IP, which adds latency the planner can never
recover. The other common option sends raw EtherCAT commands and leaves
smoothing and coordination to ROS2, which is not built for hard
real-time work. Both approaches become the limiting factor once a line
needs production-grade cycle accuracy. The WMX ROS2 package closes the
gap by bringing the WMX motion control engine into ROS2, so the
planner's output runs as smooth and deterministic motion without
leaving the ROS2 ecosystem.

What is WMX ROS2?
----------------------------------------

WMX ROS2 is an open source MIT-licensed ROS2 package layer that owns
the timing-sensitive step, smoothing trajectories, coordinating joints,
and emitting commands at the rate servo drivers expect. It runs in
simulation, in hardware-in-the-loop, and on real EtherCAT hardware
across x86 industrial PCs and NVIDIA Jetson boards on a real-time Linux
kernel (PREEMPT_RT). It is built on the WMX motion control engine,
which keeps motion on a deterministic cycle. WMX exposes more than 200 APIs
for trajectory conversion, EtherCAT configuration, I/O, and engine
control on a deterministic real-time cycle, with profiles such as
Position Velocity Time (PVT) and multi-axis coordinated motion. Proven
over a decade in semiconductor equipment, manufacturing lines, and
precision robotics, WMX runs free in 1-hour sessions that continue by
restarting EtherCAT, while a commercial license removes the limit for
production use.




Where to go next
----------------------------------------

* Follow the :doc:`getting_started/index` guide to set up the environment and run the package.
* See :doc:`integration/integration` for current and planned integration scenarios.
* Refer to the :doc:`api_reference/api_reference` for ROS2 services, topics, and actions.
* Consult :doc:`support` for common issues and their resolutions.







.. toctree::
   :maxdepth: 3

   getting_started/index
   integration/integration
   packages/packages
   api_reference/api_reference
   support
   about