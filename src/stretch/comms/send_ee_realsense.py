import copy
import io

import cv2
import zmq

from stretch.hardware.sensors.d405 import D405


def initialize(camarr_port, camb64_port, exposure: str = "low"):
    # zeromq
    ctx = zmq.Context()
    camarr_sock = ctx.socket(zmq.PUB)
    camarr_sock.setsockopt(zmq.SNDHWM, 1)
    camarr_sock.setsockopt(zmq.RCVHWM, 1)
    camarr_sock.bind(f"tcp://*:{camarr_port}")
    camb64_sock = ctx.socket(zmq.PUB)
    camb64_sock.setsockopt(zmq.SNDHWM, 1)
    camb64_sock.setsockopt(zmq.RCVHWM, 1)
    camb64_sock.bind(f"tcp://*:{camb64_port}")

    # opencv camera
    camera = D405(exposure)

    return camarr_sock, camb64_sock, camera


def send_imagery_as_numpy_arr(sock, camera: D405):
    msg = camera.get_message()
    sock.send_pyobj(msg)
    return msg


def send_imagery_as_base64_str(sock, message: dict):
    msg = copy.copy(message)
    did_encode_rgb, buffer_rgb = cv2.imencode(".jpg", msg["color_image"])
    did_encode_dpt, buffer_dpt = cv2.imencode(".jp2", msg["depth_image"])
    msg["color_image"] = buffer_rgb
    msg["depth_image"] = buffer_dpt
    if not did_encode_rgb or not did_encode_dpt:
        print("Warning: failed to encode d405 wrist cam image. Skipping...")
        return
    sock.send_pyobj(msg)
