import cv2
import typing
import numpy
import mediapipe

class MediaPipeFaceDetection:
    
    # The mediapipe link https://google.github.io/mediapipe/solutions/selfie_segmentation.html
    
    def __init__(
                self,
                confidence: float = 0.25, #confidence if face
                mediapipe_utilise_draw: bool = True,
                color = (255, 175, 80),
                thickness: int = 2,
                model_selection: bool = 1, #type of model 1 = gen - 0 = landscape mode
                ):

        self.mediapipe_utilise_draw = mediapipe_utilise_draw
        self.color = color
        self.thickness = thickness
        self.mp_drawing = mediapipe.solutions.drawing_utils
        self.mp_face_detection = mediapipe.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(model_selection=model_selection, 
                                                                   min_detection_confidence=confidence)



    def tlbr(self, frame, mp_detections: typing.List):
        # Return coorinates in array of TopLeftBottomRight tlbr
        
        detections = []
        frame_height, frame_width, _ = frame.shape
        for detection in mp_detections:
            left = max(0 ,int(detection.location_data.relative_bounding_box.xmin * frame_width))
            top = max(0 ,int(detection.location_data.relative_bounding_box.ymin * frame_height))    
            height = int(detection.location_data.relative_bounding_box.height * frame_height)
            width = int(detection.location_data.relative_bounding_box.width * frame_width)
            detections.append([top, left, top + height, left + width])

        return numpy.array(detections)



    def __call__(self, frame, return_tlbr = False): 

        results = self.face_detection.process(frame)
        
        if return_tlbr:
            if results.detections:
                return self.tlbr(frame, results.detections)
            return []

        if results.detections:
            if self.mediapipe_utilise_draw:
                for detection in results.detections:
                    self.mp_drawing.draw_detection(frame, detection)
            
            else:
                for tlbr in self.tlbr(frame, results.detections):
                    cv2.rectangle(frame, tlbr[:2][::-1], tlbr[2:][::-1], self.color, self.thickness)
        
        return frame