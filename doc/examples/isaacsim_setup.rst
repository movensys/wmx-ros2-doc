NVIDIA Isaac Setup (Optional)
=============================

This setup is optional — skip it if you only run on the real robot or with
Gazebo. It is needed for two NVIDIA components used by the examples:

- **Isaac Sim** — the desktop simulator that renders the robot for the
  Simulation and HIL modes. Set up :ref:`isaac-sim-desktop` if you run any
  ``*_simulation`` or ``*_hil`` scene.
- **Isaac ROS** — the GPU-accelerated perception base images used by the
  ``isaac-ros_*`` build flavors (cuMotion, Nvblox, YOLO). Set up
  :ref:`isaac-ros` if you build the manipulator container with
  ``MOVENSYS_ROS_VERSION=isaac-ros_4.1`` or ``isaac-ros_3.2``.

Both require an NVIDIA GPU and Ubuntu 22.04 or 24.04.

.. _isaac-sim-desktop:

Isaac Sim Desktop Setup
-----------------------

1. Download
~~~~~~~~~~~

Download `Isaac Sim 5.0.0
<https://docs.isaacsim.omniverse.nvidia.com/5.0.0/installation/index.html>`_
(the ``isaac-sim-standalone-5.0.0-linux-x86_64.zip`` package).

2. Install
~~~~~~~~~~

.. code-block:: bash

   mkdir ~/isaacsim
   cd ~/Downloads
   unzip "isaac-sim-standalone-5.0.0-linux-x86_64.zip" -d ~/isaacsim
   cd ~/isaacsim
   ./post_install.sh

3. Configure the ROS 2 bridge environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the following to your ``~/.bashrc``:

.. code-block:: bash

   export ROS_DISTRO=jazzy                 # {jazzy, humble}
   source /opt/ros/$ROS_DISTRO/setup.bash
   export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/$ROS_DISTRO/lib

4. Run with the ROS 2 bridge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   ~/isaacsim/isaac-sim.selector.sh

In the Isaac Sim App Selector, make sure the **ROS Bridge Extension** is set to
``isaacsim.ros2.bridge``, then click **Start**.

.. _isaac-ros:

Isaac ROS Setup
---------------

Required only for the ``isaac-ros_*`` build flavors. Because the RTX 50xx GPU
driver is not supported by the Ubuntu *desktop* installer, install Ubuntu
**Server** first and add the desktop afterwards. Pick the tab that matches your
``MOVENSYS_ROS_VERSION``.

.. tab-set::

   .. tab-item:: isaac-ros_4.1 (Ubuntu 24.04 / Jazzy)

      **1. Set up the NVIDIA workspace:**

      .. code-block:: bash

         mkdir -p ~/workspaces/isaac_ros-dev/src
         echo 'export ISAAC_ROS_WS="${ISAAC_ROS_WS:-${HOME}/workspaces/isaac_ros-dev/}"' >> ~/.bashrc
         source ~/.bashrc

      Configure the Isaac ROS apt repository:

      .. code-block:: bash

         locale  # check for UTF-8
         sudo apt update && sudo apt install locales
         sudo locale-gen en_US en_US.UTF-8
         sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
         export LANG=en_US.UTF-8

         sudo apt update && sudo apt install curl gnupg
         sudo apt install software-properties-common
         sudo add-apt-repository universe
         sudo apt-get update

         k="/usr/share/keyrings/nvidia-isaac-ros.gpg"
         curl -fsSL https://isaac.download.nvidia.com/isaac-ros/repos.key | sudo gpg --dearmor | sudo tee -a $k > /dev/null
         f="/etc/apt/sources.list.d/nvidia-isaac-ros.list"
         sudo touch $f
         s="deb [signed-by=$k] https://isaac.download.nvidia.com/isaac-ros/release-4.1 noble main"
         grep -qxF "$s" $f || echo "$s" | sudo tee -a $f
         sudo apt-get update

      Initialize the Isaac ROS CLI:

      .. code-block:: bash

         pip install termcolor --break-system-packages
         sudo apt-get install isaac-ros-cli

      **2. Install Docker** — see `Install Docker Engine on Ubuntu
      <https://docs.docker.com/engine/install/ubuntu/>`_, then allow Docker
      without ``sudo``:

      .. code-block:: bash

         sudo usermod -aG docker $USER
         newgrp docker
         sudo chmod 666 /var/run/docker.sock
         sudo systemctl restart docker

      **3. Install the NVIDIA Container Toolkit** — install and configure per the
      `NVIDIA Container Toolkit guide
      <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html>`_,
      install `Git LFS <https://git-lfs.com/>`_, and restart Docker:

      .. code-block:: bash

         sudo apt-get install git-lfs
         git lfs install --skip-repo
         sudo systemctl daemon-reload && sudo systemctl restart docker

      **4. Initialize and activate the Isaac ROS container:**

      .. code-block:: bash

         sudo isaac-ros init docker
         isaac-ros activate

   .. tab-item:: isaac-ros_3.2 (Ubuntu 22.04 / Humble)

      **1. Install Docker** — see `Install Docker Engine on Ubuntu
      <https://docs.docker.com/engine/install/ubuntu/>`_, then allow Docker
      without ``sudo``:

      .. code-block:: bash

         sudo usermod -aG docker $USER
         newgrp docker
         sudo chmod 666 /var/run/docker.sock

      **2. Install the NVIDIA Container Toolkit** — install and configure per the
      `NVIDIA Container Toolkit guide
      <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html>`_,
      then restart Docker and install `Git LFS <https://git-lfs.com/>`_:

      .. code-block:: bash

         sudo systemctl daemon-reload && sudo systemctl restart docker
         sudo apt-get install git-lfs
         git lfs install --skip-repo

      **3. Set up and test the Isaac ROS container:**

      .. code-block:: bash

         mkdir -p ~/workspaces/isaac_ros-dev/src
         export ISAAC_ROS_WS=${HOME}/workspaces/isaac_ros-dev/

         cd ${ISAAC_ROS_WS}/src && \
           git clone -b release-3.2 https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git
         cd $ISAAC_ROS_WS && ./src/isaac_ros_common/scripts/run_dev.sh

      Verify the images were pulled:

      .. code-block:: bash

         docker image list

      You should see ``isaac_ros_dev-x86_64:latest`` and ``x86_64-image:latest``.

.. _isaac-scenes:

Scenes
------

The ready-to-open USD scenes come from the
`movensys-simulation <https://github.com/movensys/movensys-simulation>`_
repository. Clone it alongside the manipulator workspace:

.. code-block:: bash

   mkdir -p ~/workspaces
   cd ~/workspaces
   git clone https://github.com/movensys/movensys-simulation.git

Scenes are organized under ``dobot_cr3a/`` and ``dobot_cr5a/`` and named
``<n><mode>_<example>.usd``, where the mode suffix selects how the robot is
driven:

.. list-table::
   :header-rows: 1
   :widths: 12 20 68

   * - Suffix
     - Mode
     - Purpose
   * - ``a``
     - simulation
     - Pure Isaac Sim — no physical hardware needed
   * - ``b``
     - hil
     - Hardware-in-the-loop — simulation with the WMX runtime
   * - ``c``
     - real
     - Visualization against the real robot

The CR3A directory provides scenes for the trajectory, AprilTag pick-and-place,
obstacle avoidance, RoboPoly, and AprilTag obstacle-avoidance examples; the CR5A
directory currently provides the trajectory scene. In the App Selector
(``Play``), open a scene such as
``~/workspaces/movensys-simulation/dobot_cr3a/3a_trajectory_simulation.usd``,
click **Play**, then run the matching manipulator scenario to drive the robot.
