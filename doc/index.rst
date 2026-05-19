WMX ROS2 Documentation
=======================

Welcome to the WMX ROS2 documentation. This project provides ROS2
packages for controlling robot platforms through the WMX motion control
engine over EtherCAT. It is intended for applications that require deterministic, high precision
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
* Multimodal large language models (LLMs) and vision language models
  (VLMs) for natural language task specification and high level reasoning

The entire stack runs on a single industrial PC (IPC) or edge device
without a separate motion controller.

.. figure:: /_static/images/wmx-ros2_overview.drawio.png
   :alt: wmx-ros2 architecture overview
   :align: center
   :width: 100%

   wmx-ros2 architecture overview.

Overview
----------------------------------------

In a ROS2 motion stack a planner such as MoveIt2 or Nav2 generates a
trajectory and `ros2_control <https://control.ros.org/>`_ sends joint
commands to the hardware. Turning those commands into the precisely timed
signals that motors actually execute is the harder step and ROS2 alone
does not provide it.

Most setups address this with a closed industrial controller over TCP/IP
which adds latency, or with raw EtherCAT commands which leave trajectory
smoothing to the planner. Both become limiting when timing precision
matters.

wmx-ros2 fills this gap by connecting the WMX motion control engine to
ROS2 so the planner's output runs as smooth and deterministic motion
while staying inside the ROS2 ecosystem.

What is wmx-ros2?
----------------------------------------

wmx-ros2 is an open source, MIT licensed ROS2 package that handles the
timing sensitive parts of robot motion: smoothing trajectories,
coordinating multiple joints, and generating commands at the rate that the
hardware expects.

wmx-ros2 runs in simulation, in hardware in the loop configurations, and
on real EtherCAT hardware. Supported platforms include x86 PCs and NVIDIA
Jetson boards running a real time Linux kernel (PREEMPT_RT).

What is WMX?
----------------------------------------

WMX is the motion control engine that wmx-ros2 is built on. It exposes
more than 200 APIs covering trajectory conversion, EtherCAT network
configuration, I/O, and engine control, all on a deterministic real-time
cycle. WMX has over a decade of deployment in semiconductor equipment,
manufacturing lines, and precision robotics, and supports motion profiles
such as Position Velocity Time (PVT) and multi axis coordinated motion.

The free license runs in 6 hour sessions and continues by restarting the
EtherCAT communication. A separate commercial license removes this limit
for business and production use.




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