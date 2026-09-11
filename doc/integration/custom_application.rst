Building Custom Applications
=============================

Overview
--------

The WMX R2 packages expose standard ROS2 interfaces (actions, services, and
topics) that any ROS2 node can interact with. You can build custom applications
in **Python** or **C++** that control the robot without modifying the WMX R2
source code.

The system is designed for EtherCAT servo
drives. The ROS2 interface layer is independent of the specific robot model --
only the configuration files and WMX parameter files are robot-specific.

There are three approaches to controlling the robot:

1. **High-level pose/joint services** -- Call the ``/wmx/moveit2/*`` services
   provided by the ``moveit2_api`` node in
   `movensys-manipulator <https://github.com/movensys/movensys-manipulator>`_
   for MoveIt2-planned Cartesian and joint moves (see
   :doc:`moveit2_integration`). This is the simplest option when MoveIt2 is
   running.
2. **Trajectory-based** -- Send a full trajectory to the
   ``FollowJointTrajectory`` action server (used by MoveIt2 and custom
   planners)
3. **Direct axis control** -- Publish velocity or position commands to
   individual axes via topics (used for low-level or real-time control)

The examples below focus on approaches 2 and 3, which use the ``wmx_r2_package``
interfaces directly.

Prerequisites
-------------

Before building a custom application:

- WMX R2 packages are installed and built
  (see :doc:`../getting_started/index`)
- The WMX R2 nodes are running (either the manipulator launch or
  the general launch)
- Your workspace is sourced: ``source ~/workspaces/movensys_ws/install/setup.bash``
- You have a basic understanding of ROS2 actions, services, and topics

Available Interfaces
--------------------

.. list-table:: Actions
   :header-rows: 1
   :widths: 40 35 25

   * - Name
     - Type
     - Node
   * - ``/movensys_manipulator_arm_controller/follow_joint_trajectory``
     - ``control_msgs/action/FollowJointTrajectory``
     - ``joint_trajectory_controller``

.. list-table:: Key Services
   :header-rows: 1
   :widths: 30 30 40

   * - Name
     - Type
     - Purpose
   * - ``/wmx/engine/get_engine_status``
     - ``std_srvs/srv/Trigger``
     - Query engine state
   * - ``/wmx/lifecycle/get_node_states``
     - ``wmx_r2_message/srv/GetNodeStates``
     - Check which nodes are ``active``
   * - ``/wmx/set_gripper``
     - ``std_srvs/srv/SetBool``
     - Open/close gripper
   * - ``/wmx/axes/set_servo_on``
     - ``wmx_r2_message/srv/SetAxes``
     - Enable/disable servos
   * - ``/wmx/axes/start_pos`` / ``start_mov``
     - ``wmx_r2_message/srv/StartAxesPose``
     - Absolute / relative single-axis move
   * - ``/wmx/axes/start_vel`` / ``start_jog``
     - ``wmx_r2_message/srv/StartAxesVelocity``
     - Constant velocity / dead-man jog
   * - ``/wmx/axes/stop``
     - ``wmx_r2_message/srv/SetAxes``
     - Decelerate to a stop; never blocked

.. important::

   **Single-axis motion is a service call, not a topic publish.** There is no
   motion topic. And while a controller listed in ``motion_controllers`` is
   ``active``, ``start_pos``, ``start_mov``, ``start_vel``, ``start_jog``, and
   ``start_home`` all answer ``success: false`` — the controller owns the
   axes. An application that plans should go through the
   ``FollowJointTrajectory`` action, not through these.

.. list-table:: Key Topics
   :header-rows: 1
   :widths: 30 30 15 25

   * - Name
     - Type
     - Rate
     - Purpose
   * - ``/joint_states``
     - ``sensor_msgs/msg/JointState``
     - 100 Hz
     - Current joint positions and velocities
   * - ``/wmx/axes/status``
     - ``wmx_r2_message/msg/AxesStatus``
     - 100 Hz
     - Detailed axis status (alarms, limits, torques)
   * - ``/moveit2_trajectory/execution_active``
     - ``std_msgs/msg/Bool``
     - On change
     - Latched: true while a planned goal is running

For complete field-level documentation, see :doc:`../api_reference/ros2_actions`,
:doc:`../api_reference/ros2_services`, and :doc:`../api_reference/ros2_topics`.

Python Example: Send a Trajectory
-----------------------------------

This example creates a ROS2 Python node that sends a two-point trajectory to
the ``FollowJointTrajectory`` action server. The robot moves from the current
position to the specified joint targets.

.. code-block:: python

   #!/usr/bin/env python3
   """Send a joint trajectory to the WMX R2 joint_trajectory_controller."""

   import rclpy
   from rclpy.action import ActionClient
   from rclpy.node import Node
   from control_msgs.action import FollowJointTrajectory
   from trajectory_msgs.msg import JointTrajectoryPoint
   from builtin_interfaces.msg import Duration


   class TrajectoryClient(Node):
       def __init__(self):
           super().__init__('trajectory_client')
           self._client = ActionClient(
               self,
               FollowJointTrajectory,
               '/movensys_manipulator_arm_controller/follow_joint_trajectory'
           )

       def send_trajectory(self, positions, duration_sec=3):
           """Send a trajectory that moves to the given joint positions.

           Args:
               positions: List of 6 joint angles in radians.
               duration_sec: Time to reach the target in seconds.
           """
           self.get_logger().info('Waiting for action server...')
           self._client.wait_for_server()

           goal = FollowJointTrajectory.Goal()
           goal.trajectory.joint_names = [
               'joint1', 'joint2', 'joint3',
               'joint4', 'joint5', 'joint6'
           ]

           # Start point (current position -- use zeros or read from /joint_states)
           start_point = JointTrajectoryPoint()
           start_point.positions = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
           start_point.time_from_start = Duration(sec=0, nanosec=0)

           # Target point
           target_point = JointTrajectoryPoint()
           target_point.positions = positions
           target_point.time_from_start = Duration(sec=duration_sec, nanosec=0)

           goal.trajectory.points = [start_point, target_point]

           self.get_logger().info(
               f'Sending trajectory: {positions} over {duration_sec}s'
           )
           future = self._client.send_goal_async(
               goal, feedback_callback=self._feedback_cb
           )
           future.add_done_callback(self._goal_response_cb)

       def _goal_response_cb(self, future):
           goal_handle = future.result()
           if not goal_handle.accepted:
               self.get_logger().error('Goal rejected')
               return
           self.get_logger().info('Goal accepted, waiting for result...')
           result_future = goal_handle.get_result_async()
           result_future.add_done_callback(self._result_cb)

       def _result_cb(self, future):
           result = future.result().result
           if result.error_code == 0:
               self.get_logger().info('Trajectory executed successfully')
           else:
               self.get_logger().error(
                   f'Trajectory failed with error code: {result.error_code}'
               )
           rclpy.shutdown()

       def _feedback_cb(self, feedback_msg):
           # The WMX server does not publish feedback during execution
           pass


   def main():
       rclpy.init()
       client = TrajectoryClient()

       # Move to target: joint1=0.5rad, joint2=-0.3rad, others at 0
       client.send_trajectory([0.5, -0.3, 0.2, 0.0, 0.1, 0.0], duration_sec=3)

       rclpy.spin(client)


   if __name__ == '__main__':
       main()

**Run the example** (with the manipulator nodes already running):

.. code-block:: bash

   python3 trajectory_client.py

.. warning::

   This sends real motion commands. Ensure the robot workspace is clear
   before running.

**Key constraints** (from the action server source code):

- Maximum **1000 waypoints** per trajectory
- The first point's ``time_from_start`` is forced to zero by the server
- If the last point is within 1 ms of the previous point, it is dropped
- Only ``positions`` and ``time_from_start`` are used by the WMX engine
- The server blocks until motion completes (no intermediate feedback)

C++ Example: Send a Trajectory
-------------------------------

This example follows the same pattern used by ``wmx_core_motion_node.cpp``
in the workspace. It creates an action client, sends a trajectory goal, and
waits for the result.

.. code-block:: cpp

   #include <memory>
   #include <chrono>

   #include "rclcpp/rclcpp.hpp"
   #include "rclcpp_action/rclcpp_action.hpp"
   #include "control_msgs/action/follow_joint_trajectory.hpp"
   #include "trajectory_msgs/msg/joint_trajectory_point.hpp"

   using FollowJointTrajectory = control_msgs::action::FollowJointTrajectory;
   using GoalHandleFJT = rclcpp_action::ClientGoalHandle<FollowJointTrajectory>;
   using namespace std::chrono_literals;

   int main(int argc, char **argv)
   {
     rclcpp::init(argc, argv);
     auto node = rclcpp::Node::make_shared("trajectory_client_cpp");

     auto client = rclcpp_action::create_client<FollowJointTrajectory>(
       node,
       "/movensys_manipulator_arm_controller/follow_joint_trajectory"
     );

     // Wait for action server
     if (!client->wait_for_action_server(10s)) {
       RCLCPP_ERROR(node->get_logger(), "Action server not available");
       return 1;
     }

     // Build goal
     auto goal = FollowJointTrajectory::Goal();
     goal.trajectory.joint_names = {
       "joint1", "joint2", "joint3", "joint4", "joint5", "joint6"
     };

     // Start point
     trajectory_msgs::msg::JointTrajectoryPoint start_pt;
     start_pt.positions = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
     start_pt.time_from_start = rclcpp::Duration(0, 0);

     // Target point at 3 seconds
     trajectory_msgs::msg::JointTrajectoryPoint target_pt;
     target_pt.positions = {0.5, -0.3, 0.2, 0.0, 0.1, 0.0};
     target_pt.time_from_start = rclcpp::Duration(3, 0);

     goal.trajectory.points = {start_pt, target_pt};

     RCLCPP_INFO(node->get_logger(), "Sending trajectory goal...");

     auto send_goal_options =
       rclcpp_action::Client<FollowJointTrajectory>::SendGoalOptions();
     send_goal_options.result_callback =
       [&node](const GoalHandleFJT::WrappedResult &result) {
         if (result.result->error_code == 0) {
           RCLCPP_INFO(node->get_logger(), "Trajectory executed successfully");
         } else {
           RCLCPP_ERROR(node->get_logger(), "Trajectory failed: error_code=%d",
                        result.result->error_code);
         }
         rclcpp::shutdown();
       };

     client->async_send_goal(goal, send_goal_options);
     rclcpp::spin(node);
     return 0;
   }

To build this in your own package, add these dependencies to your
``package.xml``:

.. code-block:: xml

   <depend>rclcpp</depend>
   <depend>rclcpp_action</depend>
   <depend>control_msgs</depend>
   <depend>trajectory_msgs</depend>

And in ``CMakeLists.txt``:

.. code-block:: cmake

   find_package(rclcpp REQUIRED)
   find_package(rclcpp_action REQUIRED)
   find_package(control_msgs REQUIRED)
   find_package(trajectory_msgs REQUIRED)

   add_executable(trajectory_client src/trajectory_client.cpp)
   ament_target_dependencies(trajectory_client
     rclcpp rclcpp_action control_msgs trajectory_msgs)

Python Example: Read Robot State
---------------------------------

This example subscribes to ``/joint_states`` and prints the current joint
positions. The ``joint_state_broadcaster`` node publishes this topic at 100 Hz
with 8 values (6 joints + 2 gripper fingers).

.. code-block:: python

   #!/usr/bin/env python3
   """Subscribe to /joint_states and print joint positions."""

   import rclpy
   from rclpy.node import Node
   from sensor_msgs.msg import JointState


   class JointStateReader(Node):
       def __init__(self):
           super().__init__('joint_state_reader')
           self._sub = self.create_subscription(
               JointState, '/joint_states', self._callback, 10
           )

       def _callback(self, msg):
           # msg.name: 8 names (joint1-6 + picker_1_joint, picker_2_joint)
           # msg.position: 8 values in radians
           # msg.velocity: 8 values in rad/s (gripper velocities are always 0.0)
           joint_positions = dict(zip(msg.name, msg.position))
           self.get_logger().info(
               f'Positions: ' +
               ', '.join(f'{n}={p:.4f}' for n, p in joint_positions.items())
           )


   def main():
       rclpy.init()
       node = JointStateReader()
       rclpy.spin(node)
       node.destroy_node()
       rclpy.shutdown()


   if __name__ == '__main__':
       main()

**Run the example:**

.. code-block:: bash

   python3 joint_state_reader.py

Expected output (values depend on current robot position):

.. code-block:: text

   [joint_state_reader] Positions: joint1=0.0012, joint2=-0.3021, joint3=0.1500, joint4=0.0003, joint5=0.0998, joint6=-0.0001, picker_1_joint=0.0000, picker_2_joint=0.0000

Python Example: Monitor Axis State and Control Gripper
-------------------------------------------------------

This example shows how to query the engine status, monitor detailed axis
diagnostics, and control the gripper -- combining services and topics.

.. code-block:: python

   #!/usr/bin/env python3
   """Query engine status and control gripper."""

   import rclpy
   from rclpy.node import Node
   from std_srvs.srv import Trigger, SetBool


   class RobotController(Node):
       def __init__(self):
           super().__init__('robot_controller')
           self._status_client = self.create_client(
               Trigger, '/wmx/engine/get_engine_status'
           )
           self._gripper_client = self.create_client(
               SetBool, '/wmx/set_gripper'
           )

       def get_engine_status(self):
           """Query the WMX3 engine state."""
           self._status_client.wait_for_service()
           future = self._status_client.call_async(Trigger.Request())
           rclpy.spin_until_future_complete(self, future)
           result = future.result()
           self.get_logger().info(f'Engine status: {result.message}')
           return result.message

       def set_gripper(self, close: bool):
           """Open or close the gripper.

           Args:
               close: True to close, False to open.
           """
           self._gripper_client.wait_for_service()
           request = SetBool.Request()
           request.data = close
           future = self._gripper_client.call_async(request)
           rclpy.spin_until_future_complete(self, future)
           result = future.result()
           self.get_logger().info(
               f'Gripper: success={result.success}, {result.message}'
           )
           return result.success


   def main():
       rclpy.init()
       controller = RobotController()

       # Check engine is communicating
       status = controller.get_engine_status()
       if status != 'Communicating':
           controller.get_logger().error(
               f'Engine not ready (state: {status}). '
               'Launch the manipulator nodes first.'
           )
           rclpy.shutdown()
           return

       # Close gripper, wait, then open
       controller.set_gripper(close=True)
       import time; time.sleep(2.0)
       controller.set_gripper(close=False)

       controller.destroy_node()
       rclpy.shutdown()


   if __name__ == '__main__':
       main()

Using with MoveIt2 Python API
-------------------------------

If MoveIt2 is installed and configured for your robot, you can use the
``MoveGroupInterface`` to plan and execute trajectories. MoveIt2 internally
sends goals to the same ``FollowJointTrajectory`` action server.

.. code-block:: python

   #!/usr/bin/env python3
   """MoveIt2 Python example using moveit_py."""

   import rclpy
   from rclpy.node import Node


   def main():
       rclpy.init()
       node = Node('moveit2_example')

       # MoveIt2 Python bindings (moveit_py) require the MoveIt configuration
       # package for your robot to be available.
       #
       # The typical workflow is:
       # 1. Launch the WMX R2 manipulator nodes (provides /joint_states)
       # 2. Launch MoveIt2 with your robot's config package
       # 3. Use MoveGroupInterface to plan and execute
       #
       # Example using the MoveIt2 Python API:
       #
       #   from moveit.planning import MoveItPy
       #   moveit = MoveItPy(node_name="moveit_py_node")
       #   arm = moveit.get_planning_component("manipulator_arm")
       #   arm.set_start_state_to_current_state()
       #   arm.set_goal_state(configuration_name="home")
       #   plan = arm.plan()
       #   if plan:
       #       arm.execute()

       node.get_logger().info(
           'MoveIt2 integration requires:\n'
           '  1. WMX R2 manipulator nodes running\n'
           '  2. MoveIt2 config package for your robot\n'
           '  3. MoveIt2 move_group node running\n'
           'See: ros2 launch <your_moveit_config> move_group.launch.py'
       )

       node.destroy_node()
       rclpy.shutdown()


   if __name__ == '__main__':
       main()

MoveIt2 handles trajectory planning, collision avoidance, and sends the
result to the ``joint_trajectory_controller`` via the
``FollowJointTrajectory`` action. See
:doc:`moveit2_integration` for configuration details.

Direct Axis Control
--------------------

For applications that need single-axis motion without trajectory planning,
call the ``/wmx/axes/*`` services on ``wmx_core_motion_node``.

.. important::

   **These are services, not topics.** Every one of them returns
   ``success`` and a per-axis ``message``, and every one of them is refused
   while a controller listed in ``motion_controllers`` is ``active``. Read
   the response — a silent publish that does nothing is not a failure mode
   here, but a ``success: false`` you ignored is.

.. code-block:: python

   #!/usr/bin/env python3
   """Direct axis control through the /wmx/axes/* services."""

   import rclpy
   from rclpy.node import Node
   from wmx_r2_message.srv import SetAxes, StartAxesPose, StartAxesVelocity


   class DirectAxisControl(Node):
       def __init__(self):
           super().__init__('direct_axis_control')
           self._pos = self.create_client(StartAxesPose, '/wmx/axes/start_pos')
           self._mov = self.create_client(StartAxesPose, '/wmx/axes/start_mov')
           self._vel = self.create_client(StartAxesVelocity, '/wmx/axes/start_vel')
           self._stop = self.create_client(SetAxes, '/wmx/axes/stop')

           for client in (self._pos, self._mov, self._vel, self._stop):
               if not client.wait_for_service(timeout_sec=10.0):
                   raise RuntimeError(
                       f'{client.srv_name} not available. '
                       'Is wmx_core_motion_node active?'
                   )

       def _call(self, client, request):
           future = client.call_async(request)
           rclpy.spin_until_future_complete(self, future)
           response = future.result()
           if not response.success:
               self.get_logger().error(
                   f'{client.srv_name} refused: {response.message}'
               )
           return response.success

       def move_absolute(self, axes, targets, vel=5.0, acc=10.0, dec=10.0):
           """Move to an absolute target, in axis user units."""
           req = StartAxesPose.Request()
           req.axis = axes
           req.target = targets
           req.velocity = [vel] * len(axes)
           req.acc = [acc] * len(axes)
           req.dec = [dec] * len(axes)
           return self._call(self._pos, req)

       def move_relative(self, axes, displacements, vel=5.0, acc=10.0, dec=10.0):
           """Move by a displacement from wherever the axes are now."""
           req = StartAxesPose.Request()
           req.axis = axes
           req.target = displacements
           req.velocity = [vel] * len(axes)
           req.acc = [acc] * len(axes)
           req.dec = [dec] * len(axes)
           return self._call(self._mov, req)

       def move_velocity(self, axes, velocities, acc=10.0, dec=10.0):
           """Run at constant velocity until stopped. Sign selects direction."""
           req = StartAxesVelocity.Request()
           req.axis = axes
           req.velocity = velocities
           req.acc = [acc] * len(axes)
           req.dec = [dec] * len(axes)
           return self._call(self._vel, req)

       def stop(self, axes):
           """Decelerate to a stop. Never blocked by a controller."""
           req = SetAxes.Request()
           req.axis = axes
           req.data = [0] * len(axes)
           return self._call(self._stop, req)


   def main():
       rclpy.init()
       ctrl = DirectAxisControl()

       ctrl.move_relative([0], [10.0])    # +10 user units on axis 0
       ctrl.stop([0])

       ctrl.destroy_node()
       rclpy.shutdown()


   if __name__ == '__main__':
       main()

Taking the axes from a controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If these calls return ``success: false`` with a message about a controller,
a motion controller is active and owns the axes. Deactivate it first:

.. code-block:: python

   from wmx_r2_message.srv import SetNodeState

   client = node.create_client(SetNodeState, '/wmx/lifecycle/set_node_state')
   req = SetNodeState.Request()
   req.node_name = 'joint_trajectory_controller'
   req.transition = 'deactivate'

.. warning::

   Do **not** deactivate ``joint_state_broadcaster`` to free the axes. It
   switches the servos **off** when it deactivates, which drops an arm's
   holding torque. Deactivate the motion controller instead.

.. important::

   Direct axis commands require the axes to be initialized first: servo
   enabled, command mode set, and homed. The manipulator launch does this
   through ``joint_state_broadcaster``; from the general nodes alone, run the
   startup sequence in :doc:`../api_reference/ros2_services` first.

.. warning::

   These service calls cause **immediate physical motion** and bypass MoveIt2
   collision checking.

Adapting for Different Robots
-------------------------------------

WMX R2 is robot-agnostic by construction: no robot is baked into any launch
file. Supporting a new EtherCAT manipulator means writing two files — a ROS
parameter YAML and a WMX parameter XML — and passing them as launch
arguments. No source changes, and no new launch file.

Configuration files to create or modify
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - File
     - Changes Required
   * - **YAML config** (e.g., ``new_robot_config.yaml``)
     - Set ``joint_axes``, ``joint_name`` list, ``joint_feedback_rate``,
       gripper values, topic names, and ``wmx_param_file_path``
   * - **WMX XML parameters** (e.g., ``new_robot_wmx_parameters.xml``)
     - Define gear ratios, axis polarities, encoder modes, homing parameters,
       and limit switch settings for each servo axis
   * - **Launch file**
     - Nothing to write. ``wmx_r2_manipulator.launch.py`` and
       ``wmx_r2_differential.launch.py`` take the YAML and XML as arguments,
       so a new robot is a new pair of files, not a new launch file.
   * - **ESI files** (``/opt/wmx3/ESI/``)
     - Add the EtherCAT Slave Information file for any servo drive model the
       WMX Runtime does not already ship

Steps to adapt
^^^^^^^^^^^^^^^

1. **Identify your servo drives** -- Determine the vendor and product IDs of
   each EtherCAT servo drive in your robot, and check that a matching ESI file
   is present in ``/opt/wmx3/ESI/``.

2. **Create the WMX parameter file** -- Copy ``cr3a_wmx_parameters.xml`` and
   modify gear ratios, polarities, and encoder settings for your servo drives.
   The gear ratio maps encoder counts to radians:
   ``numerator = encoder_counts_per_revolution``,
   ``denominator = 2 * pi (6.28319)``.

3. **Create the YAML config** -- Copy ``example/cr3a_manipulator_config.yaml``
   and update. ``joint_axes`` and ``joint_name`` must be the **same lists, in
   the same order**, in all three motion nodes:

   .. code-block:: yaml

      joint_state_broadcaster:
        ros__parameters:
          joint_axes: [0, 1, 2, 3, 4, 5]   # WMX axis indices
          joint_feedback_rate: 100         # Hz
          joint_name: ["joint1", "joint2", "joint3",
                       "joint4", "joint5", "joint6"]
          gripper_joint_name: ["picker_1_joint", "picker_2_joint"]
          encoder_joint_topic: /joint_states

      joint_trajectory_controller:
        ros__parameters:
          joint_axes: [0, 1, 2, 3, 4, 5]
          joint_name: ["joint1", "joint2", "joint3",
                       "joint4", "joint5", "joint6"]
          joint_trajectory_action: /my_robot_arm_controller/follow_joint_trajectory

      wmx_lifecycle_manager_node:
        ros__parameters:
          managed_nodes:                   # device-level nodes first
            - wmx_core_motion_node
            - wmx_io_node
            - wmx_ethercat_node
            - joint_state_broadcaster
            - joint_trajectory_controller
            - joint_position_controller

   The XML path is **not** set here — it is passed to the launch file as
   ``wmx_param_file``, which injects it as ``wmx_param_file_path``.

4. **Launch it** -- No new launch file. Pass your two files as arguments:

   .. code-block:: bash

      wros ros2 launch wmx_r2_package wmx_r2_manipulator.launch.py \
          use_sim_time:=false \
          config_file:=/abs/path/to/new_robot_config.yaml \
          wmx_param_file:=/abs/path/to/new_robot_wmx_parameters.xml

5. **Update URDF/SRDF** (if using MoveIt2) -- Create a MoveIt2 configuration
   package for your robot with the correct kinematics, joint limits, and
   collision geometry. ``joint_trajectory_action`` must match the controller
   name in the MoveIt2 controllers YAML.

6. **Commission it** -- Verify the parameters, then run the low-speed
   single-axis procedure before any coordinated motion. See
   :doc:`../try_your_robot/index`.

What stays the same
^^^^^^^^^^^^^^^^^^^^

- Every node executable and every launch file — the robot is data, not code
- All service and topic names
- The ``FollowJointTrajectory`` action interface
- The ``wmx_r2_message`` custom interface types
- The build process

See :doc:`../api_reference/wmx_r2_package` for node and parameter details
and :doc:`../api_reference/wmx_r2_message` for the custom interface types.
