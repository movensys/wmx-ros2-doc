Install WMX ROS2
====================

WMX3 is MOVENSYS's software-defined motion control stack.
It connects a PC to servo drives via Lan cable and provides deterministic cycle loop.

We recommend to :bi:`verify basic behavior in a simulator` (WMX3, Isaac Sim, Gazebo, etc.)
before moving to real motor control testing on robot control machine.

Prerequisites
-----------------

1. Ubuntu 22.04/24.04 LTS
#. ``sudo`` privileges

Install WMX 
--------------------

Select the tab that matches your hardware.

.. tab-set::

   .. tab-item:: x86-based PC
      :sync: x86

      **Download the WMX3 Installer**

      Select the archive that matches your Ubuntu version.

      *Ubuntu 22.04*

      .. code-block:: bash

         wget --user=guest --password=guest http://download.movensys.com:8111/webdav/WMX3_Installer/Linux/Ubuntu22.04_linux5.19.0_rt10.zip

      *Ubuntu 24.04*

      .. code-block:: bash

         wget --user=guest --password=guest http://download.movensys.com:8111/webdav/WMX3_Installer/Linux/Ubuntu24.04_linux6.15.2_rt2.zip

      .. note::

         If the wget command fails, download the archive directly via the URL using a web browser.

      .. list-table::
         :widths: 30 70
         :header-rows: 1

         * - Ubuntu version
           - Download via URL
         * - Ubuntu 22.04
           - `Ubuntu22.04_linux5.19.0_rt10.zip <http://download.movensys.com:8111/webdav/WMX3_Installer/Linux/Ubuntu22.04_linux5.19.0_rt10.zip>`_
         * - Ubuntu 24.04
           - `Ubuntu24.04_linux6.15.2_rt2.zip <http://download.movensys.com:8111/webdav/WMX3_Installer/Linux/Ubuntu24.04_linux6.15.2_rt2.zip>`_

      .. note::

         The download page may prompt for credentials. Use ***guest*** for both
         username and password.

      **Install WMX3**

      Once the archive is downloaded, extract it and run the installer.

      *Ubuntu 22.04*

      .. code-block:: bash

         unzip Ubuntu22.04_linux5.19.0_rt10.zip
         cd Ubuntu22.04_linux5.19.0_rt10
         sudo dpkg -i *wmx3-installer.deb

      *Ubuntu 24.04*

      .. code-block:: bash

         unzip Ubuntu24.04_linux6.15.2_rt2.zip
         cd Ubuntu24.04_linux6.15.2_rt2
         sudo dpkg -i *wmx3-installer.deb

   .. tab-item:: ARM-based PC
      :sync: arm

      Installing WMX3 on an ARM machine is for real-world scenarios.

      **Download the WMX3 Installer**

      Unzip ``wmx3_arm64_installers.zip`` from the download site.

      .. code-block:: bash

         wget --user=guest --password=guest http://download.movensys.com:8111/webdav/WMX3_Installer/Linux/wmx3_arm64_installers.zip
         unzip wmx3_arm64_installers.zip

      Currently supported IPCs are listed below.

      1. Advantech MIC-713, NVIDIA Jetson Orin NX on Ubuntu 20.04

      .. code-block:: bash

         sudo dpkg -i 20260403_Ubuntu20.04_linux-5.10.120-rt70-jetson-orin-nx-mic-713-wmx3-installer.deb

      2. Advantech MIC-733ao, NVIDIA Jetson Orin AGX on Ubuntu 22.04

      .. code-block:: bash

         sudo dpkg -i 20260403_Ubuntu22.04_linux-5.15.148-rt-jetson-agx-orin-mic-733ao-wmx3-installer.deb

      .. note:: Recommended NIC driver for the ``5.15.148-tegra`` kernel

         For the ``5.15.148-tegra`` kernel, we also recommend using ``rt_igb.ko``
         from ``rt_igc_igb_5.15.148-rt-tegra.zip``:

         .. code-block:: bash

            wget --user=guest --password=guest http://download.movensys.com:8111/webdav/WMX3_Installer/Linux/rt_igc_igb_5.15.148-rt-tegra.zip
            unzip rt_igc_igb_5.15.148-rt-tegra.zip

         After unzipping, copy the ``rt_igb.ko`` or ``rt_igc.ko`` file to
         ``/opt/wmx3/platform/ethercat``:

         .. code-block:: bash

            cp rt_igc.ko rt_igb.ko /opt/wmx3/platform/ethercat

      3. Advantech MIC-743, NVIDIA Jetson Thor on Ubuntu 24.04

      .. code-block:: bash

         sudo dpkg -i 20260403_Ubuntu24.04_linux-6.8.12-rt-jetson-thor-mic-743-wmx3-installer.deb

The installer places the WMX3 runtime at ``/opt/wmx3/``.
Confirm the required headers and libraries are present:

.. code-block:: bash

   ls /opt/wmx3/include/WMX3Api.h
   ls /opt/wmx3/lib/libwmx3api.so
   ls /opt/wmx3/lib/libimdll.so

All files must exist before proceeding. If any are missing, re-run the
installer or contact your MOVENSYS representative.

.. note:: 

   Our product depends on Network Interface Card (NIC) drivers, not on specific IPCs.
   If you share Ubuntu kernel version and NIC driver information to issue boards (https://github.com/movensys/wmx-ros2/issues),
   we can support WMX3 installation for your environment.

   Check your kernel version:

   .. code-block:: bash

      uname -a

   Check your NIC drivers:

   .. code-block:: bash

      lspci -v




Install WMX ROS2 Package
------------------------------

Add the following to your ``~/.bashrc``:

.. code-block:: bash

   export ROS_DOMAIN_ID=70                         #use any number
   export ROS_DISTRO=jazzy                         #support {jazzy, humble}
   export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

   source /opt/ros/$ROS_DISTRO/setup.bash
   source ~/workspaces/movensys_ws/install/setup.bash

Apply the changes:

.. code-block:: bash

   source ~/.bashrc


Install Required ROS2 Dependencies
----------------------------------------------

.. code-block:: bash

   sudo apt update
   sudo apt install -y ros-${ROS_DISTRO}-graph-msgs \
                    ros-${ROS_DISTRO}-moveit-ros \
                    ros-${ROS_DISTRO}-moveit-planners \
                    ros-${ROS_DISTRO}-moveit-plugins \
                    ros-${ROS_DISTRO}-moveit-setup-assistant \
                    ros-${ROS_DISTRO}-moveit-configs-utils \
                    ros-${ROS_DISTRO}-moveit-task-constructor-core \
                    ros-${ROS_DISTRO}-ros2-control \
                    ros-${ROS_DISTRO}-ros2-controllers \
                    ros-${ROS_DISTRO}-rmw-cyclonedds-cpp
   sudo apt install -y python3-colcon-common-extensions python3-rosdep


Create Workspace and Build
--------------------------

**Create workspace**

.. code-block:: bash

   mkdir -p ~/workspaces/movensys_ws/src
   cd ~/workspaces/movensys_ws/src && \
   git clone https://github.com/movensys/wmx-ros2.git

**Rosdep update**

.. code-block:: bash

   sudo rosdep init   # only needed once per system
   rosdep update
   cd ~/workspaces/movensys_ws
   rosdep install --from-paths src --ignore-src -y

**Build** (``wmx_ros2_package`` depends on ``wmx_ros2_message``, so build the
message package first):

.. code-block:: bash

   cd ~/workspaces/movensys_ws

   # Stage 1: build the message package first
   colcon build --packages-select wmx_ros2_message
   source install/setup.bash

   # Stage 2: build all remaining packages
   colcon build
   source install/setup.bash


Verify Installation
-------------------

.. code-block:: bash

   ros2 pkg list | grep wmx && ros2 pkg executables wmx_ros2_package

Expected:

.. code-block:: text

   wmx_ros2_message
   wmx_ros2_package
   wmx_ros2_package diff_drive_controller
   wmx_ros2_package follow_joint_trajectory_server
   wmx_ros2_package manipulator_state
   wmx_ros2_package wmx_core_motion_node
   wmx_ros2_package wmx_engine_node
   wmx_ros2_package wmx_ethercat_node
   wmx_ros2_package wmx_io_node



