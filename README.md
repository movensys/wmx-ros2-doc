# WMX R2 Documentation

**WMX R2™ — turn Physical AI decisions into precise industrial motion.**

Technical documentation for **WMX R2**, which brings the ROS 2 ecosystem into
deterministic real-time industrial motion control. It connects a ROS 2 interface
to the [MOVENSYS](https://www.movensys.com/) WMX3 motion engine and drives
industrial servos over EtherCAT. ("R2" stands for *Real-time Robotics*.)

**Documentation site:** https://movensys.github.io/wmx-r2-doc/

> ROS is a trademark of Open Robotics.

## What WMX R2 does

- **Turns planner output into servo motion.** MoveIt2 and Nav2 trajectories
  become precisely timed commands on a fixed cycle over EtherCAT. In the
  See-Think-Act loop of Physical AI, WMX R2 is the *Act* layer.
- **Drives any EtherCAT machine, regardless of brand.** It commands the drives
  directly with CoE and controls axes rather than a specific robot model, so a
  six-axis arm, a mobile base and a custom multi-axis machine are all driven the
  same way.
- **Runs the entire stack on a single edge device.** Motion is software, so no
  external motion controller and no motion-control card are needed. x86-64 and
  arm64 alike, from an industrial PC to an NVIDIA Jetson Thor.
- **Keeps the ROS 2 ecosystem you already use.** MoveIt2, Nav2, ros2_control,
  Intel OpenVINO, NVIDIA Isaac Sim and Isaac ROS, Gazebo, YOLO, and multimodal
  LLMs and VLMs.
- **Is built for production, not the bench.** Deterministic cycle timing,
  servo-level error handling and direct drive access, with 85% lower mean
  absolute tracking error than a conventional external controller.
- **Is free to start with.** The WMX engine runs in free 6-hour sessions, and
  the ROS 2 interface is MIT-licensed.

## Documentation Contents

| Section | Description |
|---------|-------------|
| **Getting Started** | Computer setup, WMX Runtime install, and building the WMX R2 packages (container or native) |
| **Example Applications** | Testing WMX R2 on the general nodes, Isaac Sim setup, and the manipulator, navigation, and Robopoly walkthroughs in Simulation / HIL / Real modes |
| **Integration** | MoveIt2, NVIDIA Isaac cuMotion, Nav2, custom planner, custom application, and the VLM/LLM layer |
| **Commissioning** | Robot parameter configuration and validation, first-motion procedure, safety responsibilities, validated-hardware matrix |
| **API Reference** | ROS2 services, topics, and actions, plus `wmx_r2_message`, `wmx_r2_package`, and `wmx_r2_control` |
| **Support** | Troubleshooting by symptom |
| **Licensing** | Boundary between the MIT-licensed ROS 2 interface and the proprietary WMX engine |

The documentation tracks these repositories:

| Repository | Role |
|------------|------|
| [wmx-r2](https://github.com/movensys/wmx-r2) | ROS2 interface to the WMX3 motion engine |
| [movensys-manipulator](https://github.com/movensys/movensys-manipulator) | MoveIt2 / cuMotion planning and Nvblox / YOLO / AprilTag perception |
| [movensys-navigation](https://github.com/movensys/movensys-navigation) | Nav2 planning, EKF odometry, and SLAM for a differential-drive base |
| [movensys-intelligence](https://github.com/movensys/movensys-intelligence) | VLM / Whisper layer and the Robopoly sample application |
| [movensys-simulation](https://github.com/movensys/movensys-simulation) | Isaac Sim USD scenes used by the examples |

## Building Locally

### Prerequisites

- Python 3.10+

### Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r doc/requirements.txt
```

### Build

```bash
cd doc
make clean
make html
```
Open `doc/_build/html/index.html` in your browser to view the documentation.

### Webserver 
- Youtube link is broken when you try to see index.html file to web browser directly.

```bash
cd doc/_build/html
python3 -m http.server 8000
```

## Deployment

Documentation is automatically built and deployed to GitHub Pages via GitHub Actions on every push to `main`.


## License

This documentation: Copyright 2026 MOVENSYS. All rights reserved.

"WMX R2" as a whole is **not** MIT-licensed. The licensing boundary is:

| Component | License |
|-----------|---------|
| ROS 2 interface source code (`wmx_r2_message`, `wmx_r2_package`, `wmx_r2_control`) and the example repositories | MIT |
| WMX Motion Engine, WMX3 SDK, and binaries (`/opt/wmx3/`) | Proprietary — evaluation or commercial license |
| This documentation | © 2026 MOVENSYS, all rights reserved |

The MIT-licensed packages link against the proprietary SDK and cannot be built
or run without a WMX runtime. See the
[Licensing](https://movensys.github.io/wmx-r2-doc/licensing.html) page.

