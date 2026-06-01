Computer Setup
==============

WMX ROS2 needs a real-time Linux kernel, ROS 2, and the WMX Runtime on the
target computer before you install the ROS2 packages. The target can be a
standard **desktop** (x86), an **Intel IPC** such as the Advantech UNO-258
(x86), or an **Advantech MIC** edge platform (NVIDIA Jetson, arm64). This page
covers installing the operating system, getting a PREEMPT_RT kernel in place,
verifying latency, installing ROS 2, and configuring the WMX Runtime.

Supported targets
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 14 22 18 16

   * - Target
     - Arch
     - Ubuntu
     - RT kernel
     - OS install
   * - Desktop
     - x86_64
     - 22.04 / 24.04
     - PREEMPT_RT
     - Standard installer
   * - Intel IPC (Advantech UNO-258)
     - x86_64
     - 22.04 / 24.04
     - PREEMPT_RT
     - Standard installer
   * - Advantech MIC-713
     - arm64
     - 22.04
     - ``5.15.148-rt``
     - Flash (Jetson)
   * - Advantech MIC-733ao
     - arm64
     - 22.04
     - ``5.15.148-rt``
     - Flash (Jetson)
   * - Advantech MIC-743
     - arm64
     - 24.04 (JetPack 7.0)
     - ``6.8.12-rt``
     - Flash (Jetson)

Install the operating system
----------------------------

**Desktop / Intel IPC (Advantech UNO-258, x86):** install Ubuntu 22.04 or 24.04
the usual way with the standard Ubuntu installer (including its real-time
kernel).

**Advantech MIC (Jetson, arm64):** the MIC boards ship without a real-time
kernel, so you build and flash a prebuilt PREEMPT_RT image using the steps
below.

1. Connect the IPC (Advantech MIC)
----------------------------------

On a desktop machine, prepare the board's setup bundle and put the board into
recovery mode. Pick your target:

.. tab-set::

   .. tab-item:: Desktop / Intel IPC (x86)

      Not applicable — x86 targets do not flash a kernel. Install Ubuntu the
      usual way (including its real-time kernel), then continue to the
      :ref:`verification step <computer-setup-verify>`:

      - Ubuntu 22.04 LTS — `download <https://releases.ubuntu.com/jammy/>`_
      - Ubuntu 24.04 LTS — `download <https://releases.ubuntu.com/noble/>`_

   .. tab-item:: MIC-713

      **Prepare the setup files [Desktop]** — make a workspace and place the
      board's setup bundle (kernel-build/flash scripts) inside it:

      .. code-block:: bash

         mkdir ~/mic713_ubuntu2204_setup
         cd mic713_ubuntu2204_setup

      **Enter recovery mode [IPC]** — push and hold **REC**, push **RST** and
      release, wait ~8 s, then release **REC**. Confirm the desktop sees it:

      .. code-block:: bash

         lsusb   # expect a line containing: NVIDIA Corp. APX

   .. tab-item:: MIC-733ao

      .. note::

         Install an additional M.2 NVMe SSD in the board before starting due to
         limited storage capacity.

      **Prepare the setup files [Desktop]** — make a workspace and place the
      board's setup bundle (kernel-build/flash scripts) inside it:

      .. code-block:: bash

         mkdir ~/mic733_ubuntu2204_setup
         cd mic733_ubuntu2204_setup

      **Enter recovery mode [IPC]** — with power off, hold **REC** (``SW_REC1``);
      apply power and press **RST** (``SW_RST1``) once while holding ``SW_REC1``
      for 5–10 s, then release. Use a USB type-A to Micro-USB cable. Confirm:

      .. code-block:: bash

         lsusb   # expect a line containing: NVIDIA Corp. APX

   .. tab-item:: MIC-743

      **Prepare the setup files [Desktop]** — make a workspace and place the
      board's setup bundle (kernel-build/flash scripts) inside it:

      .. code-block:: bash

         mkdir ~/mic743_ubuntu2404_setup
         cd mic743_ubuntu2404_setup

      **Enter recovery mode [IPC]** — push and hold **REC**, push **RST** and
      release, wait ~8 s, then release **REC**. Confirm the desktop sees it:

      .. code-block:: bash

         lsusb   # expect a line containing: NVIDIA Corp. APX

2. Build the RT kernel [Desktop]
--------------------------------

Make the bundle scripts executable and build the kernel. Pick your target:

.. tab-set::

   .. tab-item:: Desktop / Intel IPC (x86)

      Not applicable — x86 targets use the kernel from the standard Ubuntu
      install. Continue to the :ref:`verification step <computer-setup-verify>`.

   .. tab-item:: MIC-713

      Download the setup material (including the kernel-build/flash ``.sh``
      scripts) into the workspace created in step 1:

      - `MIC-713 Ubuntu 22.04 setup files <https://softservogroup-my.sharepoint.com/my?csf=1&web=1&e=jE7ImF&id=%2Fpersonal%2Fmfikih%5Fmovensys%5Fcom%2FDocuments%2FMIC%2D713%20Ubuntu%2022%2E04&FolderCTID=0x012000B151A254E50D934D86D4E7D8A20B5881>`_
      - `MIC-713 (S)-OX4A1 6.1.0 package <https://softservogroup.sharepoint.com/sites/rnd-LMX/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2Frnd%2DLMX%2FShared%20Documents%2FLMX%2FMIC%2D713%2FMIC%2D713%28S%29%2DOX4A1%2F6%2E1%2E0&viewid=d96db33b%2Dd591%2D40e6%2D8d8b%2De28fafb22b39&e=5%3A62565d4591264fd7a123045b74ca8afe&sharingv2=true&fromShare=true&at=9&CID=99612995%2Df964%2D4069%2D002d%2D4fa01cfa0feb&FolderCTID=0x012000035A31A124A36C45B5417DD6D08E57E1&ovuser=d824d7cb%2D8b07%2D470f%2Db893%2Daaeb2a457183%2Cmfikih%40movensys%2Ecom&OR=Teams%2DHL&CT=1747194077702&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiIxNDE1LzI1MDQxNzE5MzA5IiwiSGFzRmVkZXJhdGVkVXNlciI6ZmFsc2V9>`_

      Then make the scripts executable and build the kernel:

      .. code-block:: bash

         sudo chmod +x *.sh
         ./code_MIC713.sh
         ./build_eval_713.sh

      In the kernel ``menuconfig`` that opens, set:

      - General setup → Timer subsystem → Timer tick handling → **Full dynticks
        system (tickless)**
      - General setup → Preemption Model: **Fully Preemptible Kernel (RT)**
      - Kernel Features → Timer frequency: **1000 HZ**
      - Device Drivers → Network device support → Ethernet driver support →
        Realtek devices → ``<M>`` **Realtek 8169/8168/8101/8125 ethernet
        support** (toggle with the space key)
      - then **save and exit**

   .. tab-item:: MIC-733ao

      Download the setup material (including the kernel-build/flash ``.sh``
      scripts) into the workspace created in step 1:

      - `MIC-733ao Ubuntu 22.04 setup files <https://softservogroup-my.sharepoint.com/my?csf=1&web=1&e=aR5ViQ&id=%2Fpersonal%2Fmfikih%5Fmovensys%5Fcom%2FDocuments%2FMIC%2D733ao%20Ubuntu%2022%2E04&FolderCTID=0x012000B151A254E50D934D86D4E7D8A20B5881>`_
      - `MIC-733ao package <https://softservogroup.sharepoint.com/sites/rnd-LMX/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2Frnd%2DLMX%2FShared%20Documents%2FLMX%2FMIC%2D733&viewid=d96db33b%2Dd591%2D40e6%2D8d8b%2De28fafb22b39&sharingv2=true&fromShare=true&at=9&CID=99612995%2Df964%2D4069%2D002d%2D4fa01cfa0feb&FolderCTID=0x012000035A31A124A36C45B5417DD6D08E57E1&ovuser=d824d7cb%2D8b07%2D470f%2Db893%2Daaeb2a457183%2Cmfikih%40movensys%2Ecom&OR=Teams%2DHL&CT=1747194077702&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiIxNDE1LzI1MDQxNzE5MzA5IiwiSGFzRmVkZXJhdGVkVXNlciI6ZmFsc2V9>`_

      Then make the scripts executable and build the kernel:

      .. code-block:: bash

         sudo chmod +x *.sh
         ./code_MIC733.sh
         ./build_eval_733.sh

      In the kernel ``menuconfig`` that opens, set:

      - General setup → Timer subsystem → Timer tick handling → **Full dynticks
        system (tickless)**
      - General setup → Preemption Model: **Fully Preemptible Kernel (RT)**
      - Kernel Features → Timer frequency: **1000 HZ**
      - Device Drivers → Network device support → Ethernet driver support →
        Realtek devices → ``<M>`` **Realtek 8169/8168/8101/8125 ethernet
        support** (toggle with the space key)
      - then **save and exit**

   .. tab-item:: MIC-743

      Download the setup material (including the kernel-build/flash ``.sh``
      scripts) into the workspace created in step 1:

      - `MIC-743 Ubuntu 24.04 setup files <https://softservogroup-my.sharepoint.com/my?id=%2Fpersonal%2Fmfikih%5Fmovensys%5Fcom%2FDocuments%2FMIC%2D743%20Ubuntu%2024%2E04&viewid=96402766%2Db04c%2D4c41%2D9f40%2D13485a5d5d54&csf=1&FolderCTID=0x012000B151A254E50D934D86D4E7D8A20B5881>`_
      - `MIC-743 package <https://softservogroup.sharepoint.com/sites/rnd-LMX/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2Frnd%2DLMX%2FShared%20Documents%2FLMX%2FMIC%2D743&viewid=d96db33b%2Dd591%2D40e6%2D8d8b%2De28fafb22b39&sharingv2=true&fromShare=true&at=9&CID=99612995%2Df964%2D4069%2D002d%2D4fa01cfa0feb&FolderCTID=0x012000035A31A124A36C45B5417DD6D08E57E1&ovuser=d824d7cb%2D8b07%2D470f%2Db893%2Daaeb2a457183%2Cmfikih%40movensys%2Ecom&OR=Teams%2DHL&CT=1747194077702&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiIxNDE1LzI1MDQxNzE5MzA5IiwiSGFzRmVkZXJhdGVkVXNlciI6ZmFsc2V9>`_

      Then make the scripts executable and build the kernel:

      .. code-block:: bash

         sudo chmod +x *.sh
         ./code_MIC743.sh
         ./build_eval_743.sh

      In the kernel ``menuconfig`` that opens, set:

      - General setup → Timer subsystem → Timer tick handling → **Full dynticks
        system (tickless)**
      - General setup → **Configure standard kernel features (expert users)**
      - General setup → Preemption Model: **Fully Preemptible Kernel (RT)**
      - Kernel Features → Timer frequency: **1000 HZ**
      - **PCI support**
      - Device Drivers → Network device support → Ethernet driver support →
        Realtek devices → ``<M>`` **Realtek 8169/8168/8101/8125 ethernet
        support** (toggle with the space key)
      - then **save and exit**

3. Flash the RT kernel to the IPC [Desktop]
-------------------------------------------

.. tab-set::

   .. tab-item:: Desktop / Intel IPC (x86)

      Not applicable — x86 targets are not flashed. Continue to the
      :ref:`verification step <computer-setup-verify>`.

   .. tab-item:: MIC-713

      .. code-block:: bash

         ./flash_713.sh

   .. tab-item:: MIC-733ao

      .. code-block:: bash

         ./flash_733.sh

   .. tab-item:: MIC-743

      .. code-block:: bash

         ./flash_743.sh

Then remove the build artifacts:

.. tab-set::

   .. tab-item:: MIC-713 / MIC-733ao

      .. code-block:: bash

         sudo rm -rf eval-rt-713
         sudo rm -rf aarch64--glibc--stable-2022.08-1

   .. tab-item:: MIC-743

      .. code-block:: bash

         sudo rm -rf eval-rt-743

.. _computer-setup-verify:

4. Verify the real-time install [IPC]
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

5. Set the hostname [IPC]
-------------------------

.. code-block:: bash

   sudo hostnamectl set-hostname <new-host-name>
   sudo reboot

6. Jetson clocks and power [IPC]
--------------------------------

Lock the Jetson to maximum performance:

.. code-block:: bash

   sudo /usr/bin/jetson_clocks
   sudo /usr/sbin/nvpmodel -m 0

7. NIC driver config [IPC]
--------------------------

Find the EtherCAT NIC's PCI address and record it as ``Location`` in
``/opt/wmx3/platform/ethercat/PrtTcpip.ini``:

.. code-block:: bash

   lspci   # e.g. x86: 02:00.0 Ethernet controller   arm64: 0008:01:00.0 Ethernet controller

- x86 example: ``Location=2;1;0``
- arm64 example: ``Location=8;1;0;0``

8. Modify the NIC driver [IPC]
------------------------------

WMX needs a patched Realtek NIC driver for EtherCAT. Use one of:

- **Option 1** — use the prebuilt module(s) from the setup material and make
  them executable:

  .. code-block:: bash

     sudo chmod 755 wmx_r8168.ko          # MIC-733ao also: wmx_igb.ko

- **Option 2** — rebuild it from the MOVENSYS NIC-driver source with
  ``build_nic.sh``.

9. Isolate the core for WMX [IPC]
---------------------------------

Isolate CPU cores for the WMX real-time threads using the Linux core-isolation
method. On MIC-743, run the provided ``linux_scripts.zip`` scripts, using the
same ``Location`` configured in ``/opt/wmx3/platform/ethercat/PrtTcpip.ini``.

10. Install ROS 2 [IPC]
-----------------------

Install ROS 2 on the target, matching the Ubuntu version — **Jazzy** on Ubuntu
24.04, **Humble** on Ubuntu 22.04. Follow the official installation guide, then
add the CycloneDDS RMW that WMX ROS2 uses:

.. tab-set::

   .. tab-item:: Jazzy (Ubuntu 24.04)

      Follow the `ROS 2 Jazzy installation guide
      <https://docs.ros.org/en/jazzy/Installation.html>`_, then:

   .. tab-item:: Humble (Ubuntu 22.04)

      Follow the `ROS 2 Humble installation guide
      <https://docs.ros.org/en/humble/Installation.html>`_, then:
