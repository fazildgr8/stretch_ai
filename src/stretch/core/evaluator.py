import cv2


class Evaluator:
    """A basic class holding some overridable logic for evaluating input on sensors."""

    def __init__(self):
        self.camera_info = None
        self.depth_scale = None
        self._done = False

    def set_done(self):
        self._done = True

    def is_done(self):
        return self._done

    def set_camera_parameters(self, camera_info, depth_scale):
        self.camera_info = camera_info
        self.depth_scale = depth_scale

    def apply(
        self, color_image, depth_image, display_received_images: bool = True
    ) -> dict:
        assert (self.camera_info is not None) and (
            self.depth_scale is not None
        ), "ERROR: YoloServoPerception: set_camera_parameters must be called prior to apply. self.camera_info or self.depth_scale is None"
        if display_received_images:
            cv2.imshow("Received RGB Image", color_image)
            cv2.imshow("Received Depth Image", depth_image)
            cv2.waitKey(1)

        results_dict = dict()
        return results_dict
