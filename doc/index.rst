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

wmx-ros2 integrates with widely used projects in the ROS2 ecosystem:

* `MoveIt2 <https://moveit.ai/>`_ for manipulator motion planning
* `NVIDIA Isaac Sim <https://developer.nvidia.com/isaac/sim>`_ and
  `Gazebo <https://gazebosim.org/>`_ for simulation
* `NVIDIA Isaac ROS <https://developer.nvidia.com/isaac/ros>`_ for GPU
  accelerated perception
* `YOLO <https://docs.ultralytics.com/>`_ for real time object detection
* `Intel OpenVINO <https://docs.openvino.ai/>`_ for optimized inference on
  CPU and integrated accelerators
* Multimodal large language models (LLMs) and vision language models
  (VLMs) for natural language task specification and high level reasoning



.. figure:: /_static/images/wmx-ros2_overview.drawio.png
   :alt: wmx-ros2 architecture overview
   :align: center
   :width: 100%

   wmx-ros2 architecture overview.

Why need a Real-Time OS?
----------------------------------------

Industrial automation requires deterministic and high precision motion
as a baseline. The drives that move a robot expect a new command at a
fixed interval. If a command arrives
late the motion stutters, accuracy drops, and on a production line the
drives can fault and stop the machine in the middle of process. A
standard Linux kernel is built for throughput rather than keeping a
strict schedule, so it can pause the program for a few milliseconds
to handle a network packet or a background task. Those few
milliseconds are exactly what causes a missed cycle. A Real-Time OS
such as Linux with the PREEMPT_RT patch
guarantees that high priority threads for motion control
thread run when they need to, even if the rest of the system is busy.
That is why every industrial motion stack runs on top of a Real-Time
OS.

Why wmx-ros2?
----------------------------------------

A Real-Time OS handles the kernel-level guarantees, but the motion
pipeline still has a step that ROS2 alone does not cover. A planner
such as MoveIt2 or Nav2 produces a trajectory and
`ros2_control <https://control.ros.org/>`_ hands joint commands to the
hardware. Those commands still need to be translated into the precisely
timed signals that drives execute on a fixed cycle. Most ROS2 setups
close this execution gap with a closed industrial controller over
TCP/IP. That choice adds latency the planner can never recover. The
other common option sends raw EtherCAT commands and leaves smoothing
and coordination to ROS2 which is not built for hard real-time work.
Either approach becomes the limiting factor once a line needs the cycle
accuracy that production equipment depends on. The wmx-ros2 package closes the gap
by bringing the WMX motion control engine into ROS2 so the planner's
output runs as smooth and deterministic motion without leaving the ROS2
ecosystem.

What is wmx-ros2?
----------------------------------------

The wmx-ros2 is the open source MIT-licensed ROS2 package layer that owns
the timing-sensitive part of that pipeline. It smooths trajectories,
coordinates multiple joints, and emits commands at the rate the drives
expect. It runs in simulation, in hardware-in-the-loop configurations,
and on real EtherCAT hardware. Supported platforms include x86
industrial PCs and NVIDIA Jetson boards running a real-time Linux
kernel (PREEMPT_RT). The same package moves from a developer's bench to
a production cell without rewriting the motion layer.

What is WMX?
----------------------------------------

WMX is the motion control engine underneath wmx-ros2 and the reason it
can hold an industrial cycle on top of the Real-Time OS. It exposes
more than 200 APIs covering trajectory conversion, EtherCAT network
configuration, I/O, and engine control on a deterministic real-time
cycle. It supports motion profiles such as Position Velocity Time (PVT)
and multi-axis coordinated motion. WMX has over a decade of deployment
in semiconductor equipment, manufacturing lines, and precision
robotics. The free license runs in 1-hour
sessions and continues by restarting EtherCAT communication. A separate
commercial license removes this limit for business and production use.




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
   api_reference/api_reference
   support
   about