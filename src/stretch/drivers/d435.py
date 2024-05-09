import pyrealsense2 as rs

WIDTH, HEIGHT, FPS = 640, 480, 30


class D435i:
    """Wrapper for accessing data from a D435 realsense camera, used as the head camera on Stretch RE1, RE2, and RE3."""

    def __init__(self, exposure: str = "auto", camera_number: int = 0):
        self.exposure = exposure
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self._setup_camera(exposure=exposure, number=camera_number)

    def _setup_camera(self, exposure: str = "auto", number: int = 0):
        """
        Args:
            number(int): which camera to pick in order.
        """
        camera_info = [
            {
                "name": device.get_info(rs.camera_info.name),
                "serial_number": device.get_info(rs.camera_info.serial_number),
            }
            for device in rs.context().devices
        ]
        d435i_infos = []
        for info in camera_info:
            if "D435I" in info["name"]:
                d435i_infos.append(info)

        if len(d435i_infos) == 0:
            raise RuntimeError("could not find any supported d435i cameras")

        # Specifically enable the camera we want to use - make sure it's d435i
        self.config.enable_device(d435i_infos[number]["serial_number"])
        self.config.enable_stream(rs.stream.depth, WIDTH, HEIGHT, rs.format.z16, FPS)
        self.config.enable_stream(rs.stream.color, WIDTH, HEIGHT, rs.format.bgr8, FPS)
        self.profile = self.pipeline.start(self.config)

        # Create an align object to align depth frames to color frames
        self.color_stream = rs.stream.color
        self.depth_stream = rs.align(self.align_to)

        if exposure == "auto":
            # Use autoexposre
            self.stereo_sensor = (
                self.pipeline.get_active_profile().get_device().query_sensors()[0]
            )
            self.stereo_sensor.set_option(rs.option.enable_auto_exposure, True)
        else:
            default_exposure = 33000
            if exposure == "low":
                exposure_value = int(default_exposure / 3.0)
            elif exposure == "medium":
                exposure_value = 30000
            else:
                exposure_value = int(exposure)

            self.stereo_sensor = (
                self.pipeline.get_active_profile().get_device().query_sensors()[0]
            )
            self.stereo_sensor.set_option(rs.option.exposure, exposure_value)

    def get_depth_scale(self) -> float:
        """Get scaling between depth values and metric units (meters)"""
        depth_sensor = self.profile.get_device().first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()
        return depth_scale


if __name__ == "__main__":
    camera = D435i()
