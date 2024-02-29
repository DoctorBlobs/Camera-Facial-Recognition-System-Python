import cv2
import numpy
import mediapipe

class FaceSegmentation:
    
    # Does Face segmentation using MediaPipe.
    # The mediapipe link https://google.github.io/mediapipe/solutions/selfie_segmentation.html

    def __init__(
                self,
                segment_threshold: float = 0.5,
                mediapipe_model_selection: bool = 0,
                ):


        self.mediapipe_face_segment = mediapipe.solutions.selfie_segmentation.MediaPipeSegmentation(model_selection=mediapipe_model_selection)
        self.segment_threshold = segment_threshold

    def __call__(self, frame: numpy.ndarray):

        results = self.mediapipe_face_segment.process(frame)
        condition = numpy.stack((results.segmentation_mask,) * 3, axis=-1) > self.segment_threshold

        frame = numpy.where(condition, frame, cv2.resize(frame.shape[:2][::-1]))

        return frame.astype(numpy.uint8)
