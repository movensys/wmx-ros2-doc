WMX ROS2 Documentation
=======================

Welcome to the WMX ROS2 documentation. This project provides ROS2
packages for controlling robot platforms through the WMX motion control
engine over EtherCAT. 

It is intended for applications that require deterministic, high precision
motion, such as manufacturing automation, semiconductor equipment, and
surgical robotics.

wmx-ros2 integrates with widely used projects in the ROS2 ecosystem:

* `MoveIt2 <https://moveit.ai/>`_ for manipulator motion planning
* `NVIDIA Isaac Sim <https://developer.nvidia.com/isaac/sim>`_ and
  `Gazebo <https://gazebosim.org/>`_ for simulation
* `NVIDIA Isaac ROS <https://developer.nvidia.com/isaac/ros>`_ for GPU
  accelerated perception
* `YOLO <https://docs.ultralytics.com/>`_ for real time object detection
* `Intel OpenVINO <https://docs.openvino.ai/>`_ for optimized inference on
  CPU and integrated accelerators
* Multimodal large language models (LLMs) for natural language task
  specification and high level reasoning

The entire stack runs on a single industrial PC (IPC) or edge device
without a separate motion controller.

Overview
----------------------------------------

In a ROS2 motion stack, a planner such as MoveIt2 or Nav2 generates a
trajectory and `ros2_control <https://control.ros.org/>`_ sends the joint
commands to the hardware in real time. What comes next is the harder part
because those commands still need to reach the motors as precisely timed
signals and ROS2 alone does not handle this step.

Most ROS2 setups solve this in two common ways. One uses a closed
industrial controller over TCP/IP which adds latency and keeps the motion
logic outside ROS2. The other sends raw commands directly over EtherCAT
which works but leaves trajectory smoothing to the planner. Both are
practical for many cases yet become limiting when timing precision is
critical.

wmx-ros2 fills this gap. It connects the WMX motion control engine to
ROS2 so the planner's output runs as smooth and deterministic motion on
real hardware while staying inside the ROS2 ecosystem.

What is wmx-ros2?
----------------------------------------

wmx-ros2 is an open source, MIT licensed ROS2 package that handles the
timing sensitive parts of robot motion: smoothing trajectories,
coordinating multiple joints, and generating commands at the rate that the
hardware expects.

It can be used in two modes:

* **``ros2_control`` plugin mode.** Used alongside standard controllers
  such as ``JointTrajectoryController`` or ``DiffDriveController`` to
  integrate with an existing ``ros2_control`` setup.
* **Native mode.** Full trajectories are sent directly to WMX, bypassing
  the per cycle ``ros2_control`` loop for latency sensitive applications.

wmx-ros2 runs in simulation, in hardware in the loop configurations, and
on real EtherCAT hardware. Supported platforms include x86 PCs and NVIDIA
Jetson boards running a real time Linux kernel (PREEMPT_RT).

What is WMX?
----------------------------------------

WMX is the motion control engine that wmx-ros2 is built on. It exposes
more than 200 APIs that cover the full motion control stack, including
trajectory conversion, EtherCAT network configuration, I/O handling, and
engine control. The whole engine runs on a deterministic real-time cycle
to meet the timing requirements of motion hardware.

WMX has been deployed for more than a decade in industrial settings such
as semiconductor equipment, manufacturing lines, and precision robotics,
where microsecond level timing accuracy is required. It provides motion
profiling features such as Position Velocity Time (PVT) profiles and
multi axis coordinated motion.

The free license runs for 6 hours per session and continues simply by
restarting the EtherCAT communication, which makes it suitable for
development and evaluation use. A separate commercial license removes
this 6 hour limit and is intended for business and production deployment.




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