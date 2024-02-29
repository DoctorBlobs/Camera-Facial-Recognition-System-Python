import numpy
import typing
import time
import cv2

class FPScounter:
    
    def __init__(
        self, 
        range_average = 30,
        pos = (7, 70),
        thickness = 3,
        lineFont = cv2.LINE_AA,
        fontFace = cv2.FONT_HERSHEY_DUPLEX,
        color = (51, 204, 255),
        fontSize = 3
        ):
        
        
        self._range_average = range_average
        self.frame_time = 0
        self.last_frame_time = 0
        self.fps_array = []
        
        self.pos = pos
        
        self.thickness = thickness
        self.fontFace = fontFace
        self.fontSize = fontSize
        self.color = color

        self.lineFont = lineFont



    def __call__(self, frame = None):
        # Measure duration between each call and return frame with added  text FPS on it

        self.last_frame_time = self.frame_time
        self.frame_time = time.time()
        
        if not self.last_frame_time:
            return frame
        
        if frame is None:
            return fps
        
        self.fps_array.append(1/(self.frame_time - self.last_frame_time))
        self.fps_array = self.fps_array[-self._range_average:]
        
        fps = float(numpy.average(self.fps_array))

        cv2.putText(frame, str(int(fps)), 
                    self.pos, 
                    self.fontFace, 
                    self.fontSize, 
                    self.color, 
                    self.thickness, 
                    self.lineFont)
        
        return frame