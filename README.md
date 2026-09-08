# WMX R2 Documentation

**WMX R2™ — The Real-Time Execution Layer for Physical AI**

Technical documentation for **WMX R2**, a complete real-time robotics solution for Physical AI that integrate a ROS 2 interface with the [MOVENSYS](https://www.movensys.com/) WMX3 motion engine it runs on. ("R2" stands for *Real-time Robotics*.)

> ROS is a trademark of Open Robotics.

**Documentation Site:** https://movensys.github.io/wmx-r2-doc/

## Overview

WMX R2 combines a ROS 2 interface with the MOVENSYS WMX3 EtherCAT-based motion engine in a single solution, enabling control of robotic manipulators with motion planning through MoveIt2 and NVIDIA Isaac cuMotion.

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

