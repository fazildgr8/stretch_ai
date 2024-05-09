import pyrealsense2 as rs


class D435:
    """Wrapper for accessing data from a D435 realsense camera, used as the head camera on Stretch RE1, RE2, and RE3."""

    def __init__(self, exposure=1000):
        self.exposure = exposure
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self._get_camera()
        #self.config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 90)

    def _get_camera(self):
        camera_info = [
            {
                "name": device.get_info(rs.camera_info.name),
                "serial_number": device.get_info(rs.camera_info.serial_number),
            }
            for device in rs.context().devices
        ]

        print("All cameras that were found:")
        print(camera_info)


if __name__ == '__main__':
    camera = D435()
