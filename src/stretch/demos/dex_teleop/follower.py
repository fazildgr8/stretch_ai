#!/usr/bin/env python

import argparse
import pprint as pp

import numpy as np
import zmq

import stretch.demos.dex_teleop.dex_teleop_parameters as dt
import stretch.demos.dex_teleop.gripper_to_goal as gg
import stretch.demos.dex_teleop.send_d405_images as send_d405_images
import stretch.motion.simple_ik as si
import stretch.utils.loop_stats as lt


class DexTeleopFollower:
    def __init__(
        self,
        robot_speed,
        starting_configuration,
        robot_allowed_to_move,
        using_stretch_2,
        scaling: float = 0.5,
        gamma: float = 2.0,
        exposure: str = "low",
        send_port=5555,
    ):
        self.robot_speed = robot_speed
        self.starting_configuration = starting_configuration
        self.robot_allowed_to_move = robot_allowed_to_move
        self.using_stretch_2 = using_stretch_2
        self.gripper_to_goal = gg.GripperToGoal(
            robot_speed, starting_configuration, robot_allowed_to_move, using_stretch_2
        )

        # Initialize IK
        self.simple_ik = si.SimpleIK()

        # Define the center position for the wrist that corresponds with
        # the teleop origin.
        self.center_wrist_position = simple_ik.fk_rotary_base(center_configuration)

        goal_recv_context = zmq.Context()
        goal_recv_socket = goal_recv_context.socket(zmq.SUB)
        goal_recv_socket.setsockopt(zmq.SUBSCRIBE, b"")
        goal_recv_socket.setsockopt(zmq.SNDHWM, 1)
        goal_recv_socket.setsockopt(zmq.RCVHWM, 1)
        goal_recv_socket.setsockopt(zmq.CONFLATE, 1)
        # goal_recv_address = 'tcp://10.1.10.71:5555'
        goal_recv_address = "tcp://192.168.1.10:5555"
        goal_recv_socket.connect(goal_recv_address)

        # save the socket
        self.goal_recv_socket = goal_recv_socket
        self._done = False

        self.send_port = send_port
        self.exposure = exposure
        self.scaling = scaling
        self.gamma = gamma

        # Threads for sending and receiving commands
        self._send_thread = None
        self._recv_thread = None

    def spin_recv_commands(self):
        loop_timer = lt.LoopStats("dex_teleop_follower")
        print_timing = False
        print_goal = False

        while True:
            loop_timer.mark_start()
            goal_dict = goal_recv_socket.recv_pyobj()
            if goal_dict:
                if print_goal:
                    print("goal_dict =")
                    pp.pprint(goal_dict)
                gripper_to_goal.update_goal(**goal_dict)
            loop_timer.mark_end()
            if print_timing:
                loop_timer.pretty_print()

    def start(self):
        """Start threads for sending and receiving commands."""
        self._send_thread = threading.Thread(target=self.spin_send_images)
        self._recv_thread = threading.Thread(target=self.spin_recv_commands)
        self._done = False
        self._send_thread.start()
        self._recv_thread.start()

    def __del__(self):
        self._done = True
        if self._send_thread:
            self._send_thread.terminate()
            self._recv_thread.terminate()
            self._send_thread.join()
            self._recv_thread.join()
        self.goal_recv_socket.close()
        self.context.term()

    def spin_send_images(self):
        """Send the images here as well"""
        send_d405_images.main(
            use_remote_computer=True,
            port=self.send_port,
            exposure=self.exposure,
            scaling=self.scaling,
            gamma=self.gamma,
        )

        def spin(self):
            self.start()
            while True:
                time.sleep(0.1)


def main(args):
    use_fastest_mode = args.fast
    manipulate_on_ground = args.ground
    left_handed = args.left
    using_stretch_2 = args.stretch_2
    slide_lift_range = args.slide_lift_range

    # The 'default', 'slow', 'fast', and 'max' options are defined by
    # Hello Robot. The 'fastest_stretch_2' option has been specially tuned for
    # this application.
    #
    # WARNING: 'fastest_stretch_*' have velocities and accelerations that exceed
    # the factory 'max' values defined by Hello Robot.
    if use_fastest_mode:
        if using_stretch_2:
            robot_speed = "fastest_stretch_2"
        else:
            robot_speed = "fastest_stretch_3"
    else:
        robot_speed = "slow"

    # Note on control here
    print("Running with robot_speed =", robot_speed)

    lift_middle = dt.get_lift_middle(manipulate_on_ground)
    center_configuration = dt.get_center_configuration(lift_middle)
    starting_configuration = dt.get_starting_configuration(lift_middle)

    follower = DexTeleopFollower(
        args.robot_speed,
        args.starting_configuration,
        args.robot_allowed_to_move,
        args.using_stretch_2,
        scaling=args.scaling,
        gamma=args.gamma,
        exposure=args.exposure,
        send_port=args.send_port,
    )
    follower.spin()


if __name__ == "__main__":

    args = dt.get_arg_parser().parse_args()
    main(args)
