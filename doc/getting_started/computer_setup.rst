Computer Setup
==============

WMX ROS2 needs a real-time Linux kernel and the WMX Runtime on the target
industrial PC (IPC) before you install the ROS2 packages. This page covers
preparing the supported Advantech MIC edge platforms (NVIDIA Jetson based):
flashing a PREEMPT_RT kernel, verifying latency, and installing and licensing
the WMX Runtime.

.. note::

   The kernel-build, flash, and WMX Runtime installer files are distributed on
   the internal MOVENSYS setup share — ask your MOVENSYS contact for access.
   The literal ``lmx`` paths and binaries below (e.g. ``/opt/lmx/``) are the
   on-disk names installed by the WMX Runtime package and must be typed as
   shown.

Supported platforms
-------------------

.. list-table::
   :header-rows: 1
   :widths: 22 18 22 18 20

   * - Platform
     - Ubuntu
     - RT kernel
     - Arch
     - Setup bundle
   * - MIC-713
     - 22.04
     - ``5.15.148-rt``
     - arm64
     - ``mic713_ubuntu2204_setup``
   * - MIC-733ao
     - 22.04
     - ``5.15.148-rt``
     - arm64
     - ``mic733_ubuntu2204_setup``
   * - MIC-743
     - 24.04 (JetPack 7.0)
     - ``6.8.12-rt``
     - arm64
     - ``mic743_ubuntu2404_setup``

.. note:: **MIC-733ao only**

   Install an M.2 NVMe SSD in the board before starting.

1. Prepare the setup files [Desktop]
------------------------------------

On a desktop machine, make a workspace and place the board's setup bundle
(kernel-build/flash scripts) inside it.

.. tab-set::

   .. tab-item:: MIC-713

      .. code-block:: bash

         mkdir ~/mic713_ubuntu2204_setup
         cd mic713_ubuntu2204_setup

   .. tab-item:: MIC-733ao

      .. code-block:: bash

         mkdir ~/mic733_ubuntu2204_setup
         cd mic733_ubuntu2204_setup

   .. tab-item:: MIC-743

      .. code-block:: bash

         mkdir ~/mic743_ubuntu2404_setup
         cd mic743_ubuntu2404_setup

2. Enter recovery mode [IPC]
----------------------------

Connect a USB cable from the IPC to the desktop and put the board into recovery
mode, then confirm the desktop sees the device:

- **MIC-713 / MIC-743:** push and hold **REC**, push **RST** and release, wait
  ~8 s, then release **REC**.
- **MIC-733ao:** with power off, hold **REC** (button ``SW_REC1``); apply power
  and press **RST** (``SW_RST1``) once while holding ``SW_REC1`` for 5–10 s,
  then release. Use a USB type-A to Micro-USB cable.

.. code-block:: bash

   lsusb   # expect a line containing: NVIDIA Corp. APX

3. Build the real-time kernel [Desktop]
---------------------------------------

Make the bundle scripts executable and build the kernel:

.. tab-set::

   .. tab-item:: MIC-713

      .. code-block:: bash

         sudo chmod +x *.sh
         ./code_MIC713.sh
         ./build_eval_713.sh

   .. tab-item:: MIC-733ao

      .. code-block:: bash

         sudo chmod +x *.sh
         ./code_MIC733.sh
         ./build_eval_733.sh

   .. tab-item:: MIC-743

      .. code-block:: bash

         sudo chmod +x *.sh
         sudo ./code_MIC743.sh
         sudo ./build_eval_743.sh

In the kernel ``menuconfig`` that opens, set:

- General setup → Timer subsystem → Timer tick handling → **Full dynticks
  system (tickless)**
- General setup → Preemption Model: **Fully Preemptible Kernel (RT)**
- Kernel Features → Timer frequency: **1000 HZ**
- Device Drivers → Network device support → Ethernet driver support → Realtek
  devices → ``<M>`` **Realtek 8169/8168/8101/8125 ethernet support** (toggle
  with the space key)
- then **save and exit**

.. note:: **MIC-743 only**

   Also enable General setup → **Configure standard kernel features (expert
   users)** and **PCI support**.

4. Flash the IPC [Desktop]
--------------------------

.. tab-set::

   .. tab-item:: MIC-713

      .. code-block:: bash

         ./flash_713.sh

   .. tab-item:: MIC-733ao

      .. code-block:: bash

         ./flash_733.sh

   .. tab-item:: MIC-743

      .. code-block:: bash

         sudo ./flash_743.sh

Then remove the build artifacts:

.. tab-set::

   .. tab-item:: MIC-713 / MIC-733ao

      .. code-block:: bash

         sudo rm -rf eval-rt-713
         sudo rm -rf aarch64--glibc--stable-2022.08-1

   .. tab-item:: MIC-743

      .. code-block:: bash

         sudo rm -rf eval-rt-743

5. Verify the real-time install [IPC]
-------------------------------------

Confirm the RT kernel is running, then build and run ``cyclictest``:

.. code-block:: bash

   uname -r                  # MIC-713/733ao: 5.15.148-rt   MIC-743: 6.8.12-rt
   cat /sys/kernel/realtime  # 1
   lsb_release -a            # Ubuntu 22.04 or 24.04

   sudo apt update && sudo apt install -y build-essential git   # MIC-743: also libnuma-dev
   git clone https://git.kernel.org/pub/scm/utils/rt-tests/rt-tests.git
   cd rt-tests
   make -j
   sudo make install

   sudo taskset -c 2 cyclictest -D 60s -i 1000 p99 -m -q -h 1000 --latency=0 --priority=99 --thread --histfile=hist_cpu2.txt

.. tip::

   For a soak test, run ``stress`` across all cores in one terminal and
   ``sudo cyclictest -t -p 95`` in another for several hours, watching the max
   latency stay bounded.

6. Set the hostname [IPC]
-------------------------

.. code-block:: bash

   sudo hostnamectl set-hostname <new-host-name>   # e.g. baymax-kr
   sudo reboot                                      # reconnect over ssh with the new name

7. Jetson clocks and power [IPC]
--------------------------------

Lock the Jetson to maximum performance:

.. code-block:: bash

   sudo /usr/bin/jetson_clocks
   sudo /usr/sbin/nvpmodel -m 0

8. Install the WMX Runtime [IPC]
--------------------------------

Download the WMX Runtime installer for your board from the MOVENSYS setup share
and install it:

.. code-block:: bash

   sudo dpkg -i ./<installer-name>.deb

Find the EtherCAT NIC's PCI address and record it as ``Location`` in
``/opt/lmx/platform/ethercat/LmxTcpip.ini``:

.. code-block:: bash

   lspci   # e.g. x86: 02:00.0 Ethernet controller   arm64: 0008:01:00.0 Ethernet controller

- x86 example: ``Location=2;1;0``
- arm64 example: ``Location=8;1;0;0``

9. Modify the NIC driver [IPC]
------------------------------

- **Option 1** — use the prebuilt module(s) and make them executable:

  .. code-block:: bash

     sudo chmod 755 lmx_r8168.ko          # MIC-733ao also: lmx_igb.ko

- **Option 2** — build from source with ``build_nic.sh`` from
  `lmx_nic_driver_open
  <https://bitbucket.org/mvs_app/lmx_nic_driver_open/src/master/>`_.

10. Isolate CPU cores [IPC]
---------------------------

Isolate cores for the WMX real-time threads using the Linux core-isolation
method. On MIC-743, run the provided ``linux_scripts.zip`` scripts and use the
same ``Location`` as in ``/opt/lmx/platform/ethercat/LmxTcpip.ini``.

11. Set up the software license [IPC]
-------------------------------------

Get the computer ID and request an activation key for it:

.. code-block:: bash

   /opt/lmx/bin/lmx-get-computerid

Ask the responsible MOVENSYS contact for the license code matching that ID,
then save it:

.. code-block:: bash

   mkdir -p /opt/lmx/reg/
   cd /opt/lmx/reg/
   # create a file named SecurityCode and paste the activation key into it

With the real-time kernel verified and the WMX Runtime licensed, continue to
:doc:`install_wmx3`.
