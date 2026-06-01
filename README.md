# WMX ROS2 Documentation

Technical documentation for the **WMX ROS2** robotic manipulator control system, built on the [MOVENSYS](https://www.movensys.com/) WMX3 motion control platform.

**Documentation Site:** https://movensys.github.io/wmx-ros2-doc/

## Overview

WMX ROS2 bridges the MOVENSYS WMX3 EtherCAT-based motion controller with ROS2, enabling control of 6-DOF robotic manipulators (e.g., Dobot CR3A) with motion planning through MoveIt2 and NVIDIA Isaac cuMotion.

## Documentation Contents

| Section | Description |
|---------|-------------|
| **Getting Started** | System requirements, ROS2 installation, workspace setup, mock & physical hardware, architecture |
| **Packages** | `wmx_ros2_message` and `wmx_ros2_package` node documentation |
| **Integration** | MoveIt2, NVIDIA Isaac cuMotion, custom planner & application guides |
| **API Reference** | ROS2 services, topics, and actions |
| **Demo application** | NVIDIA Jetson Orin and Intel x86_64 setups |
| **Deployment** | Source build, Debian package, and Docker options |
| **Troubleshooting** | Common issues and solutions |

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

## Deployment

Documentation is automatically built and deployed to GitHub Pages via GitHub Actions on every push to `main`.


## License

Copyright 2026 MOVENSYS. All rights reserved.
