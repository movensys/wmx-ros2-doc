Computer Setup
==============

WMX R2 needs a real-time Linux kernel, ROS 2, and Docker on the
target computer before you install the WMX R2 packages. This page lists the
system requirements, then walks through preparing the computer step by step.

Hardware Requirements
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Component
     - Minimum
     - Recommended
   * - CPU
     - x86_64/amd64 or arm64
     - Intel Core i7 or NVIDIA Jetson Orin/Thor
   * - RAM
     - 4 GB
     - 8 GB or more
   * - Storage
     - 10 GB free
     - 20 GB free (including ROS2 + MoveIt2)
   * - NPU
     - Not required for base operation
     - Intel NPU for OpenVINO inference applications
   * - GPU
     - Not required for base operation
     - NVIDIA GPU with CUDA for Isaac cuMotion

EtherCAT Communication
~~~~~~~~~~~~~~~~~~~~~~~

EtherCAT (Ethernet for Control Automation Technology) is a real-time
industrial Ethernet fieldbus. It links the controller (the *master*) to the
servo drives and I/O modules (the *slaves*) over a single daisy-chained cable.
The master sends one frame down the chain. Each slave reads its own data and
inserts its response as the frame passes through. This updates the whole axis
network in a single pass. In an industrial EtherCAT carries the  
cyclic position and torque commands out to serovs and
returns encoder feedback every control cycle. A typical cycle runs once every
250 µs to 1 ms depending the hardware. The advantage is deterministic low-latency synchronization,
distributed clocks align all axes to within nanoseconds, cycle jitter stays
tiny, and multi-axis motion stays smooth and accurate. EtherCAT also runs over
standard Ethernet hardware and ordinary cabling. This gives the performance at
a lower wiring cost than legacy fieldbuses. 


Real-Time OS requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A servo drive needs a new command at a fixed interval, for example one
every millisecond. Regular Linux is built to get as much work done as
possible, not to hit that interval exactly, so it may pause the servo
control loop for a few milliseconds to handle a network packet or a
background job. When that happens the next command arrives late and
misses its deadline. Even one missed deadline makes the motion jerk and
lose both accuracy and speed, and on a production line it can trip the
drives and stop the machine. A real-time OS, such as Linux with the
PREEMPT_RT patch, makes sure the motion code always runs on time even
when the computer is busy. That is why industrial motion systems run on
one.

Installing this real-time kernel is covered in the setup steps below,
and configuring it for use (isolating CPU cores for the WMX real-time
threads and tuning latency) is covered in :doc:`install_wmx_runtime`.

WMX Motion Control Engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The WMX motion control engine is a high-performance, high-accuracy, real-time motion control
platform developed by MOVENSYS. It provides deterministic servo control over
EtherCAT fieldbus and serves as the hardware abstraction layer for physical servo drives.

**Key features:**

- **Real-time EtherCAT master** -- manages cyclic communication with servo
  drives at deterministic update rates
- **Multi-axis coordination** -- supports synchronized motion across 6+ servo
  axes with cubic spline interpolation (``CSplinePos``)
- **Shared-memory architecture** -- multiple ROS2 nodes connect to the same
  WMX engine instance through independent device handles, bridging the
  non-real-time ROS2 domain with the real-time WMX engine
- **Hardware abstraction** -- provides a unified C++ API (``CoreMotion``,
  ``AdvancedMotion``, ``Io``, ``Ecat``, ``WMX3Api``) so ROS2 nodes remain
  robot-agnostic; only configuration files differ between robots

The WMX runtime must be installed at ``/opt/wmx3/`` before building or
running the WMX R2 packages. See :doc:`install_wmx_runtime` for installation and
verification steps.

.. note::

   Root (sudo) access is required at runtime. The WMX motion control engine
   and EtherCAT communication require kernel-level access to the network
   interface.

The C++ standard required is **C++17** (set in ``CMakeLists.txt``).

1. Install the base OS
----------------------

Pick your target and install the operating system.

.. tab-set::

   .. tab-item:: General x86/amd64

      Install Ubuntu 22.04 or 24.04 the usual way with the standard Ubuntu
      installer, then update fully.

      - Ubuntu 22.04 LTS — `download <https://releases.ubuntu.com/jammy/>`__
      - Ubuntu 24.04 LTS — `download <https://releases.ubuntu.com/noble/>`__
      - Install guide — `Install Ubuntu desktop
        <https://ubuntu.com/tutorials/install-ubuntu-desktop#1-overview>`__

      .. code-block:: bash

         sudo apt update && sudo apt full-upgrade -y

      In firmware/BIOS, disable **Secure Boot** for now. Signing a custom
      kernel is extra work you can add later.

   .. tab-item:: Intel XPU (Core Ultra Series 3)

      Install Ubuntu 24.04 the usual way with the standard Ubuntu installer,
      then update fully.

      - Ubuntu 24.04 LTS — `download <https://releases.ubuntu.com/noble/>`__
      - Install guide — `Install Ubuntu desktop
        <https://ubuntu.com/tutorials/install-ubuntu-desktop#1-overview>`__

      .. code-block:: bash

         sudo apt update && sudo apt full-upgrade -y

      In firmware/BIOS, disable **Secure Boot** for now. Also review
      **C-states**, **SpeedStep**, and **Turbo**, plus any "low-power E-core"
      options; you will likely pin these down later for latency (see
      :ref:`core isolation <computer-setup-isolate>`).

   .. tab-item:: Jetson Developer Kit

      The Jetson developer kit's built-in eMMC storage is small — too small
      for JetPack plus ROS 2, MoveIt2, Docker images, and perception models.
      To add this storage capacity, install an NVMe SSD card in the Jetson
      developer kit's carrier board (in the M.2 Key M slot) before flashing,
      then flash the OS onto the SSD.

      Flash the board's Board Support Package (BSP) with **NVIDIA SDK
      Manager**, which installs JetPack (the L4T Linux distribution) for your
      Jetson model — Jetson Orin NX, Jetson Orin AGX, or Jetson Thor. In SDK
      Manager, select the NVMe SSD as the storage device so JetPack is
      installed on the SSD rather than the eMMC.

      - `Install Jetson with SDK Manager
        <https://docs.nvidia.com/sdk-manager/install-with-sdkm-jetson/index.html>`__

      After flashing, record the L4T release — you need it to match the
      correct real-time kernel in the next step:

      .. code-block:: bash

         cat /etc/nv_tegra_release   # e.g. R38 (release), REVISION: 4.x  ->  L4T r38.4

2. Install the real-time kernel
-------------------------------

Install a PREEMPT_RT kernel for your target.

.. tab-set::

   .. tab-item:: General x86/amd64

      Build a PREEMPT_RT kernel from the kernel.org vanilla source plus the
      official RT patch, then install the resulting ``.deb`` packages. 

      **Install build dependencies:**

      .. code-block:: bash

         sudo apt update
         sudo apt install -y build-essential libncurses-dev bison flex libssl-dev \
              libelf-dev bc zstd kmod cpio rsync git wget gnupg2 rt-tests stress-ng

      **Fetch the kernel and RT patch (with signatures):**

      Not every kernel release ships a matching RT patch. Pick a ``KVER`` that
      has one and set ``RTVER`` to its revision. Browse the
      `RT patch index <https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/>`__,
      or list the revisions available for a version from the terminal:

      .. code-block:: bash

         uname -r   # your PC's current kernel version, e.g. 6.15.2-generic
         # RT patch revisions available for a kernel version (here 6.15)
         wget -qO- https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/6.15/ | grep -oE 'patch-[0-9.]+-rt[0-9]+'

      Set the version you chose, then download it:

      .. code-block:: bash

         export KVER=6.15 RTVER=rt2
         mkdir -p ~/rt-build && cd ~/rt-build
         wget -N https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-${KVER}.tar.xz \
                 https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-${KVER}.tar.sign
         wget -N https://cdn.kernel.org/pub/linux/kernel/projects/rt/${KVER}/patch-${KVER}-${RTVER}.patch.xz \
                 https://cdn.kernel.org/pub/linux/kernel/projects/rt/${KVER}/patch-${KVER}-${RTVER}.sign

      **Verify the GPG signatures:**

      .. code-block:: bash

         gpg2 --locate-keys torvalds@kernel.org gregkh@kernel.org
         gpg2 --locate-keys bigeasy@linutronix.de
         xz -dk linux-${KVER}.tar.xz patch-${KVER}-${RTVER}.patch.xz
         gpg2 --verify linux-${KVER}.tar.sign linux-${KVER}.tar
         gpg2 --verify patch-${KVER}-${RTVER}.sign patch-${KVER}-${RTVER}.patch

      A "not certified" warning is normal.

      **Apply the patch and configure PREEMPT_RT:**

      .. code-block:: bash

         tar xf linux-${KVER}.tar && cd linux-${KVER}
         patch -p1 < ../patch-${KVER}-${RTVER}.patch
         cp /boot/config-$(uname -r) .config
         make olddefconfig
         scripts/config --disable PREEMPT_VOLUNTARY --disable PREEMPT \
                        --disable PREEMPT_DYNAMIC --enable PREEMPT_RT
         # avoid distro signing-cert traps for a personal build
         scripts/config --set-str SYSTEM_TRUSTED_KEYS "" \
                        --set-str SYSTEM_REVOCATION_KEYS ""
         scripts/config --disable MODULE_SIG
         make olddefconfig
         grep '^CONFIG_PREEMPT_RT=y' .config   # expect a match

      **Build and install the ``.deb`` packages, then reboot:**

      .. code-block:: bash

         make -j"$(nproc)" bindeb-pkg
         sudo dpkg -i ../linux-image-*${RTVER}*.deb ../linux-headers-*${RTVER}*.deb
         sudo update-grub
         sudo reboot

      .. dropdown:: Fix the NVIDIA GPU driver (only if the target has an NVIDIA GPU)
         :animate: fade-in-slide-down

         NVIDIA's kernel-module build refuses to compile against a PREEMPT_RT
         kernel: it aborts on a ``PREEMPT_RT`` presence check, so after booting
         the RT kernel the GPU comes up with no driver (``nvidia-smi`` fails).
         Rebuild the driver through DKMS with that check bypassed
         (``IGNORE_PREEMPT_RT_PRESENCE=1``). Do this while booted into the RT
         kernel, so ``uname -r`` reports it.

         Install DKMS, the open NVIDIA driver (``-open``), and confirm the RT
         kernel headers installed with the ``.deb`` packages above are present:

         .. code-block:: bash

            sudo apt install -y dkms
            sudo apt install -y nvidia-driver-580-open   # open kernel modules
            ls /lib/modules/$(uname -r)/build            # headers for the running RT kernel

         The driver source lands in ``/usr/src/nvidia-<version>/``. Add the RT
         bypass to the ``MAKE`` line of its ``dkms.conf``:

         .. code-block:: bash

            NVER=$(dpkg -l | grep -oP 'nvidia-kernel-source-\d+(-open)?\s+\K[0-9.]+' | head -1)
            sudo sed -i 's|^MAKE=.*|MAKE="IGNORE_PREEMPT_RT_PRESENCE=1 make -j$(nproc) modules SYSSRC=${kernel_source_dir}"|' \
                 /usr/src/nvidia-${NVER}/dkms.conf
            grep IGNORE_PREEMPT_RT_PRESENCE /usr/src/nvidia-${NVER}/dkms.conf   # expect a match

         Build and install the modules for the running RT kernel, then load and
         verify:

         .. code-block:: bash

            sudo dkms add "nvidia/${NVER}" 2>/dev/null || true
            sudo dkms install --force "nvidia/${NVER}" -k "$(uname -r)"
            sudo modprobe nvidia nvidia-drm nvidia-uvm
            nvidia-smi

         .. note::

            Secure Boot was disabled in the base OS step, so the freshly built
            modules load unsigned. If you later re-enable Secure Boot, enroll a
            MOK and sign the NVIDIA modules, or they will be refused at load.

   .. tab-item:: Intel XPU (Core Ultra Series 3)

      Build the RT kernel from Intel's
      `mainline-tracking <https://github.com/intel/mainline-tracking>`_ tree,
      which carries the platform enablement for current Intel silicon.

      **Install build dependencies:**

      .. code-block:: bash

         sudo apt update
         sudo apt install -y build-essential libncurses-dev bison flex libssl-dev \
              libelf-dev bc dwarves zstd git fakeroot

      **Clone the tree and check out the target branch:**

      .. code-block:: bash

         git clone https://github.com/intel/mainline-tracking.git
         cd mainline-tracking
         git checkout linux/v6.17   # or the latest v6.17 tag on that branch

      .. note::

         Intel Core Ultra Series 3 Linux support is in active flux. Pin the exact
         commit/tag you build so you can reproduce it, and expect to rebuild
         as fixes land.

      **Start from your running config plus Intel defaults, then enable RT:**

      .. code-block:: bash

         cp /boot/config-$(uname -r) .config
         make olddefconfig
         ./scripts/config --enable PREEMPT_RT
         ./scripts/config --disable PREEMPT_VOLUNTARY --disable PREEMPT --disable PREEMPT_NONE
         make olddefconfig                       # resolves the RT dependency chain
         grep PREEMPT_RT .config                 # expect CONFIG_PREEMPT_RT=y

      **Clear the distro signing keys for a personal build:**

      .. code-block:: bash

         ./scripts/config --set-str SYSTEM_TRUSTED_KEYS ""
         ./scripts/config --set-str SYSTEM_REVOCATION_KEYS ""
         make olddefconfig
         grep -E 'SYSTEM_TRUSTED_KEYS|SYSTEM_REVOCATION_KEYS' .config

      **Build the ``.deb`` packages:**

      .. code-block:: bash

         sudo apt update
         sudo apt install -y debhelper libdw-dev gawk
         make -j"$(nproc)" bindeb-pkg LOCALVERSION=-preempt-rt DPKG_FLAGS=-d
         ls -1 ~/linux-image-*preempt-rt*.deb ~/linux-headers-*preempt-rt*.deb

      **Install (clean install/rollback) and reboot:**

      .. code-block:: bash

         sudo dpkg -i ../linux-image-*preempt-rt*.deb ../linux-headers-*preempt-rt*.deb
         sudo update-grub
         sudo reboot

      **Install the AI/accelerator stack** — once the RT kernel has booted,
      install the GPU/NPU drivers and inference runtimes for the platform:

      .. code-block:: bash

         sudo bash -c "$(wget -qLO - https://raw.githubusercontent.com/open-edge-platform/edge-developer-kit-reference-scripts/refs/heads/main/main_installer.sh)"

      .. note::

         The installer targets the stock HWE kernel; on a custom RT kernel the
         DKMS driver builds should work against your installed headers, but be
         ready to install the GPU/NPU drivers manually if the script balks.

   .. tab-item:: Jetson Developer Kit

      The Jetson boards ship without a real-time kernel. Enable PREEMPT_RT by
      following NVIDIA's real-time kernel guide **for the L4T version you
      recorded** when flashing the BSP (for example, L4T r38.4):

      - `Jetson Real-Time Kernel
        <https://docs.nvidia.com/jetson/archives/r38.4/DeveloperGuide/SD/Kernel/RealTimeKernel.html>`__

      After installing and rebooting into the RT kernel, lock the board to
      maximum performance:

      .. code-block:: bash

         sudo /usr/bin/jetson_clocks
         sudo /usr/sbin/nvpmodel -m 0

      Then continue to the verification step below.

.. _computer-setup-verify:

3. Verify the real-time install
-------------------------------

Confirm the RT kernel is running, then run ``cyclictest`` to measure worst-case
latency. ``rt-tests`` was installed with the build dependencies above; on
targets where it is not present, install it with:

.. code-block:: bash

   sudo apt install -y rt-tests

.. code-block:: bash

   uname -r                  # RT kernel version (e.g. 6.15.0-rt2, or the Jetson L4T RT build)
   uname -v | grep PREEMPT_RT
   cat /sys/kernel/realtime  # 1
   lsb_release -a            # Ubuntu 22.04 or 24.04

   # baseline, then again under load (run the stressor in another terminal):
   #   stress-ng --cpu $(nproc) --io 4 --vm 2 --vm-bytes 1G --timeout 5m
   sudo cyclictest -m -S -p 90 -i 200 -d 0 -D 5m

Watch the **Max** latency. On a tuned PREEMPT_RT x86 box you typically want the
worst case in the low tens of microseconds; high spikes point to firmware/SMI
or power-management issues to chase (BIOS C-states, SpeedStep, Turbo).

.. tip::

   For a longer soak test, keep the stressor running across all cores in one
   terminal and ``cyclictest`` in another for several hours, watching the max
   latency stay bounded.

4. Set the hostname
-------------------

.. code-block:: bash

   sudo hostnamectl set-hostname <new-host-name>
   sudo reboot

5. Install ROS 2
----------------

Install ROS 2 on the target, matching the Ubuntu version: 1. **Jazzy** on Ubuntu
24.04, 2. **Humble** on Ubuntu 22.04. Follow the official installation guide, then
add the CycloneDDS RMW that WMX R2 uses.

.. tab-set::

   .. tab-item:: Jazzy (Ubuntu 24.04)

      Follow the `ROS 2 Jazzy installation guide
      <https://docs.ros.org/en/jazzy/Installation.html>`_, then install the
      CycloneDDS RMW:

      .. code-block:: bash

         sudo apt install -y ros-jazzy-rmw-cyclonedds-cpp
         echo 'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp' >> ~/.bashrc

   .. tab-item:: Humble (Ubuntu 22.04)

      Follow the `ROS 2 Humble installation guide
      <https://docs.ros.org/en/humble/Installation.html>`_, then install the
      CycloneDDS RMW:

      .. code-block:: bash

         sudo apt install -y ros-humble-rmw-cyclonedds-cpp
         echo 'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp' >> ~/.bashrc

6. Install Docker
-----------------

Docker is used to run the containerized WMX R2 and perception workloads.
Follow the `Install Docker Engine on Ubuntu<https://docs.docker.com/engine/install/ubuntu/>` instructions from the official Docker documentation, 
then add your user to the ``docker`` group so you can run Docker without ``sudo``.

**Run Docker without sudo:**

.. code-block:: bash

   sudo usermod -aG docker $USER
   newgrp docker
