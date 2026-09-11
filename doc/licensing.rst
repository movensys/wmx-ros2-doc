Licensing
=========

.. important:: **WMX R2 as a whole is not MIT-licensed.**

   "WMX R2" names a solution made of two parts with different licenses: an
   open-source ROS 2 interface, and the proprietary WMX motion engine it runs
   on. The MIT license applies to the ROS 2 interface source code, the example
   repositories, and this documentation. The WMX motion engine, its SDK, and
   its binaries are proprietary and require an evaluation or commercial
   license from MOVENSYS.

   Neither the MIT license nor the WMX license grants rights to the other.

Licensing boundary
------------------

.. list-table::
   :header-rows: 1
   :widths: 30 22 48

   * - Component
     - License
     - Notes
   * - **ROS 2 interface source code**

       ``wmx_r2_message``, ``wmx_r2_package``, ``wmx_r2_control``
     - MIT
     - Source in the ``wmx-r2`` repository. Free to use, modify, and
       redistribute under the MIT terms.
   * - **Example and reference repositories**

       ``movensys-manipulator``, ``movensys-navigation``,
       ``movensys-simulation``
     - MIT
     - Configuration, URDFs, launch files, and application nodes.
   * - **WMX Motion Engine**

       the runtime installed at ``/opt/wmx3/``
     - Proprietary: evaluation or commercial
     - Not open source. Distributed as binaries by MOVENSYS.
   * - **WMX3 SDK**

       ``WMX3Api.h``, ``libwmx3api.so``, ``libimdll.so``, ``coremotionapi``,
       ``ioapi``
     - Proprietary: evaluation or commercial
     - Required to **build** the ROS 2 interface. The MIT-licensed source
       links against these libraries; it cannot be built or run without them.
   * - **EtherCAT NIC drivers and platform modules**

       ``ec_platform.so``, ``simu_platform.so``, ``ndd_*.so``
     - Proprietary: evaluation or commercial
     - Part of the WMX runtime installation.
   * - **This documentation**
     - MIT
     - Source in the ``wmx-r2-doc`` repository. Free to use, modify, and
       redistribute under the MIT terms.

.. note::

   The MIT-licensed packages depend on the proprietary SDK at build time
   (``target_link_libraries(... coremotionapi wmx3api imdll)``). Obtaining the
   MIT source therefore does not by itself give you a buildable or runnable
   system — a WMX runtime and SDK are required as well.

WMX runtime licensing terms
----------------------------

The WMX runtime is free to evaluate in renewable 6-hour sessions; restarting
the engine starts a new session. A commercial license removes the time limit
for production use. Contact your MOVENSYS representative for commercial
licensing.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Mode
     - Terms
   * - Evaluation
     - Renewable 6-hour engine sessions, extended by restarting the engine.
       Intended for evaluation and development.
   * - Commercial
     - No session time limit. Required for production use.

Third-party components
-----------------------

WMX R2 integrates with ROS 2, MoveIt 2, Nav2, ``ros2_control``, NVIDIA Isaac
ROS and Isaac Sim, Intel OpenVINO, Ultralytics YOLO, and Gazebo. Each carries
its own license, which is unaffected by the terms above and which you are
responsible for reviewing for your deployment. Ultralytics YOLO in particular
is distributed under AGPL-3.0 unless a commercial Ultralytics license is
obtained.

ROS is a trademark of Open Robotics.

Warranty
--------

The MIT license disclaims all warranties, including merchantability and
fitness for a particular purpose, for the ROS 2 interface source code. This
disclaimer is significant in a motion-control context: the software carries no
warranty that it will produce correct or safe motion on your hardware. See
:doc:`try_your_robot/safety` for the safety functions this stack does not
provide and for where responsibility sits.
