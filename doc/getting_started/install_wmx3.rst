Install WMX R2 Package
========================

WMX R2 runs in the ``wmx_r2_container`` Docker container. The steps below set
the container up from the host; once it is running, every ROS 2 command — on
this page and throughout this documentation — goes through ``wros``, which
runs a command inside the container as **root**, with ROS 2 and the workspace
already sourced.

.. important::

   The WMX Runtime must be installed **on the host** (``/opt/wmx3/``). The
   container mounts it; it does not provide it. See :doc:`install_wmx_runtime`.

Clone the repository
--------------------

Clone first: the environment step below sources a file from inside the
repository.

.. code-block:: bash

   mkdir -p ~/workspaces/movensys_ws/src
   cd ~/workspaces/movensys_ws/src
   git clone https://github.com/movensys/wmx-r2.git

Configure the environment
-------------------------

Add the following to your ``~/.bashrc``:

.. code-block:: bash

   export ROS_DOMAIN_ID=73                         # any number; the same one everywhere
   export ROS_DISTRO=jazzy                         # {jazzy, humble}
   export CPU_ARCH=amd64                           # {amd64, arm64}
   export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

   source ~/workspaces/movensys_ws/src/wmx-r2/docker/wros.bash

.. note::

   ``ROS_DOMAIN_ID`` must be the **same value** in every container that has to
   talk to WMX R2 — the manipulator and navigation setup pages set it too. A
   mismatch is silent: the nodes start, and no ``/wmx/*`` topic is ever seen.

Apply the changes:

.. code-block:: bash

   xhost +local:docker
   source ~/.bashrc

Build and start the container
-----------------------------

.. code-block:: bash

   cd ~/workspaces/movensys_ws/src/wmx-r2/docker
   docker compose -f general.yaml -f wmx_r2.${CPU_ARCH}.yaml down
   docker compose -f general.yaml -f wmx_r2.${CPU_ARCH}.yaml build
   docker compose -f general.yaml -f wmx_r2.${CPU_ARCH}.yaml up -d

Follow the startup logs, then open a shell:

.. code-block:: bash

   docker logs wmx_r2_container -f

Called with no arguments, ``wros`` opens an interactive shell inside the
container.

.. note::

   The container and image names and the host paths — ``WMX_R2_PACKAGES``,
   ``WMX3_SDK_PATH`` — come from ``docker/.env``, relative to the ``docker/``
   directory. Edit that file if your layout differs from the default
   ``~/workspaces`` one.

Verify Installation
-------------------

.. code-block:: bash

   wros ros2 pkg list | grep wmx
   wros ros2 pkg executables wmx_r2_package

Expected:

.. code-block:: text

   wmx_r2_control
   wmx_r2_message
   wmx_r2_package
   wmx_r2_package differential_drive_controller
   wmx_r2_package gripper_controller
   wmx_r2_package joint_position_controller
   wmx_r2_package joint_state_broadcaster
   wmx_r2_package joint_trajectory_controller
   wmx_r2_package wmx_core_motion_node
   wmx_r2_package wmx_engine_node
   wmx_r2_package wmx_ethercat_node
   wmx_r2_package wmx_io_node
   wmx_r2_package wmx_lifecycle_manager_node