#!/usr/bin/env python3

# Copyright (c) Hello Robot, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the LICENSE file in the root directory
# of this source tree.
#
# Some code may be adapted from other open-source works with their respective licenses. Original
# license information maybe found below, if so.

import importlib.resources as importlib_resources
import re
import time

import numpy as np
import rerun as rr
import urchin as urdf_loader

pkg_path = str(importlib_resources.files("stretch_urdf"))
model_name = "SE3"  # RE1V0, RE2V0, SE3
tool_name = "eoa_wrist_dw3_tool_sg3"  # eoa_wrist_dw3_tool_sg3, tool_stretch_gripper, etc
urdf_file_path = pkg_path + f"/{model_name}/stretch_description_{model_name}_{tool_name}.urdf"
mesh_files_directory_path = pkg_path + f"/{model_name}/meshes"
urdf_dir = pkg_path + f"/{model_name}/"


def get_absolute_path_stretch_urdf(urdf_file_path, mesh_files_directory_path) -> str:
    """
    Generates Robot URDF with absolute path to mesh files
    """

    with open(urdf_file_path, "r") as f:
        _urdf_file = f.read()

    # find all the line which has the pattrn {file="something.type"}
    # and replace the file path with the absolute path
    pattern = r'filename="(.+?)"'
    for match in re.finditer(pattern, _urdf_file):
        orig = match.group(1)
        fn = match.group(1).split("/")[-1]
        file_path = mesh_files_directory_path + "/" + fn
        _urdf_file = _urdf_file.replace(orig, file_path)

    # Absosolute path converted streth xml
    temp_abs_urdf = "stretch_temp_abs.urdf"
    with open(urdf_dir + temp_abs_urdf, "w") as f:
        f.write(_urdf_file)
    print("Saving temp abs path stretch urdf: {}".format(urdf_dir + f"{temp_abs_urdf}"))
    return urdf_dir + temp_abs_urdf


class URDFVisualizer:
    """The `show` method in this class is modified from the
    original implementation of `urdf_loader.URDF.show`.
    """

    def __init__(self, urdf_file_path):
        self.urdf = self.urdf = urdf_loader.URDF.load(urdf_file_path)

    def get_tri_meshes(self, cfg=None, use_collision=True) -> list:
        if use_collision:
            fk = self.urdf.collision_trimesh_fk(cfg=cfg)
        else:
            fk = self.urdf.visual_trimesh_fk(cfg=cfg)
        t_meshes = {"mesh": [], "pose": []}
        for tm in fk:
            pose = fk[tm]
            t_mesh = tm.copy()
            t_meshes["mesh"].append(t_mesh)
            t_meshes["pose"].append(pose)
        return t_meshes

    def get_transform(self, cfg: dict, link_name: str) -> np.ndarray:
        """
        Get transformation matrix of the link w.r.t. the base_link
        """
        lk_cfg = {
            "joint_wrist_yaw": cfg["wrist_yaw"],
            "joint_wrist_pitch": cfg["wrist_pitch"],
            "joint_wrist_roll": cfg["wrist_roll"],
            "joint_lift": cfg["lift"],
            "joint_arm_l0": cfg["arm"] / 4,
            "joint_arm_l1": cfg["arm"] / 4,
            "joint_arm_l2": cfg["arm"] / 4,
            "joint_arm_l3": cfg["arm"] / 4,
            "joint_head_pan": cfg["head_pan"],
            "joint_head_tilt": cfg["head_tilt"],
        }
        if "gripper" in cfg.keys():
            lk_cfg["joint_gripper_finger_left"] = cfg["gripper"]
            lk_cfg["joint_gripper_finger_right"] = cfg["gripper"]
        return self.urdf.link_fk(lk_cfg, link=link_name)


class StretchURDFLogger(URDFVisualizer):
    def __init__(self) -> None:
        urdf_file = get_absolute_path_stretch_urdf(urdf_file_path, mesh_files_directory_path)
        super().__init__(urdf_file)

    def log(self):
        st = time.perf_counter()
        tm = self.get_tri_meshes()
        mesh_list = tm["mesh"]
        pose_list = np.array(tm["pose"])
        for m, p in zip(mesh_list, pose_list):
            m.apply_transform(p)
        combined_mesh = np.sum(mesh_list)
        combined_mesh.remove_duplicate_faces()
        mesh = combined_mesh
        print(f"Time to get mesh: {time.perf_counter() - st}")
        st2 = time.perf_counter()
        # breakpoint()
        rr.log(
            "world/robot/base_link",
            rr.Mesh3D(
                vertex_positions=mesh.vertices,
                triangle_indices=mesh.faces,
                vertex_normals=mesh.vertex_normals,
                # vertex_colors=vertex_colors,
                # albedo_texture=albedo_texture,
                # vertex_texcoords=vertex_texcoords,
            ),
            timeless=True,
        )
        t2 = time.perf_counter() - st2
        print(f"Time to rr log mesh: {t2}")


if __name__ == "__main__":
    urdf_logger = StretchURDFLogger()
    urdf_logger.log()