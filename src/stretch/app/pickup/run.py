#!/usr/bin/env python3

import click
import numpy as np

from stretch.agent.robot_agent import RobotAgent
from stretch.agent.zmq_client import HomeRobotZmqClient
from stretch.core import Parameters, get_parameters
from stretch.core.task import Operation, Task
from stretch.mapping.voxel import SparseVoxelMap, SparseVoxelMapNavigationSpace
from stretch.perception import create_semantic_sensor, get_encoder

from .manager import PickupManager


@click.command()
@click.option("--robot_ip", default="192.168.1.15", help="IP address of the robot")
@click.option("--recv_port", default=4401, help="Port to receive messages from the robot")
@click.option("--send_port", default=4402, help="Port to send messages to the robot")
@click.option("--reset", is_flag=True, help="Reset the robot to origin before starting")
@click.option(
    "--local",
    is_flag=True,
    help="Set if we are executing on the robot and not on a remote computer",
)
@click.option(
    "--parameter_file", default="config/default_planner.yaml", help="Path to parameter file"
)
def main(
    robot_ip: str = "192.168.1.15",
    recv_port: int = 4401,
    send_port: int = 4402,
    local: bool = False,
    parameter_file: str = "config/default_planner.yaml",
    device_id: int = 0,
    verbose: bool = False,
    show_intermediate_maps: bool = False,
    reset: bool = False,
):
    """Set up the robot, create a task plan, and execute it."""
    # Create robot
    parameters = get_parameters(parameter_file)
    robot = HomeRobotZmqClient(
        robot_ip=robot_ip,
        recv_port=recv_port,
        send_port=send_port,
        use_remote_computer=(not local),
        parameters=parameters,
    )
    _, semantic_sensor = create_semantic_sensor(
        device_id=device_id,
        verbose=verbose,
        category_map_file=parameters["open_vocab_category_map_file"],
    )

    # Start moving the robot around
    grasp_client = None

    # Agents wrap the robot high level planning interface for now
    demo = RobotAgent(robot, parameters, semantic_sensor, grasp_client=grasp_client)
    demo.start(visualize_map_at_start=show_intermediate_maps)
    if reset:
        robot.move_to_nav_posture()
        robot.navigate_to([0.0, 0.0, 0.0], blocking=True, timeout=30.0)

    # After the robot has started...
    try:
        manager = PickupManager(demo)
        task = manager.get_task(add_rotate=False)
    except Exception as e:
        print(f"Error creating task: {e}")
        robot.stop()
        return

    task.execute()

    if reset:
        # Send the robot home at the end!
        demo.go_home()

    # At the end, disable everything
    robot.stop()


if __name__ == "__main__":
    main()