import typing
import numpy
import PySimpleGUI as sg
import cv2
import tqdm
import stow


class Engine:
    # processing can be changed with custom_objects

    def __init__(
        self,
        custom_name="",
        hikvisionpwd="",
        hikvisionusr="",
        hikvisionip="",
        image_path="",
        video_path="",
        webcam_id_num: int = 0,
        show=False,
        flip_view_horizontal=False,
        flip_view_vertical=False,
        custom_objects = [],
        output_extension="out",
        start_video_frame: int = 0,
        end_video_frame: int = 0,
        stop_on_end=False,
    ):

        # Initialize Engine variables
        self.hikvisionpwd = hikvisionpwd
        self.hikvisionusr = hikvisionusr
        self.hikvisionip = hikvisionip
        self.video_path = video_path
        self.image_path = image_path
        self.webcam_id_num: int = webcam_id_num
        self.show = show
        self.flip_view_horizontal = flip_view_horizontal
        self.flip_view_vertical = flip_view_vertical
        self.custom_objects = custom_objects
        self.output_extension = output_extension
        self.start_video_frame = start_video_frame
        self.end_video_frame = end_video_frame
        self.stop_on_end = stop_on_end
        self.custom_name = custom_name

        self.layout = [
            [sg.Image(filename="", key="image")],
        ]
        self.window = sg.Window("OpenCV - Stream", layout=self.layout)

    def Engine_image(
        self, image: typing.Union[str, numpy.ndarray] = None, output_path=None
    ):
        # The function does to processing with the given image or image path

        if image is not None and isinstance(image, str):
            if not stow.exists(image):
                raise Exception(f"Given image path doesn't exist {self.image_path}")
            else:
                extension = stow.extension(image)
                if output_path is None:
                    output_path = image.replace(
                        f".{extension}", f"_{self.output_extension}.{extension}"
                    )
                image = cv2.imread(image)

        image = self.stream_processing(self.flip_cv2_stream(image))

        cv2.imwrite(output_path, image)
        self.display_cv2(image, waitTime=0)

        return image

    def Engine_cam(
        self, return_frame: bool = False
    ) -> typing.Union[None, numpy.ndarray]:
        # Create a VideoCapture object for given webcam_id_num
        cap = cv2.VideoCapture(int(self.webcam_id_num))

        print(type(cap))

        # Process webcam stream for given webcam_id_num
        print("Cap is opened: " + str(cap.isOpened()))
        print("Camera ID is: " + self.webcam_id_num)

        while cap.isOpened():
            success, frame = cap.read()
            if not success or frame is None:
                # print("Ignoring empty camera frame.")
                continue

            if return_frame:
                print("return")
                break

            frame = self.stream_processing(self.flip_cv2_stream(frame))

            if frame is None:
                print("rip")

            if not self.display_cv2(frame, waitTime=0):
                break

        else:
            raise Exception(f"Webcam with ID ({self.webcam_id_num}) can't be opened")

        cap.release()
        return frame

    def Engine_hikvision(
        self, return_frame: bool = False
    ) -> typing.Union[None, numpy.ndarray]:

        # Process webcam stream for given webcam_id_num
        print("Process Hikvision Camera")

        # Create a VideoCapture object for given webcam_id_num
        cap = cv2.VideoCapture(
            "rtsp://"
            + self.hikvisionusr
            + ":"
            + self.hikvisionpwd
            + "@"
            + self.hikvisionip
            + "/H264?ch=1&subtype=0"
        )
        # cap = cv.VideoCapture('Training\Video\Meme.mp4')
        print(
            "Accessed Camera at:"
            + self.hikvisionusr
            + ":"
            + self.hikvisionpwd
            + "@"
            + self.hikvisionip
            + "/H264?ch=1&subtype=0"
        )

        while cap.isOpened():
            success, frame = cap.read()
            if not success or frame is None:
                print("Ignoring empty camera frame.")
                continue

            if return_frame:
                break

            frame = self.stream_processing(self.flip_cv2_stream(frame))

            if not self.display_cv2(frame, webcam=True):
                break

        cap.release()
        return frame

    def Engine_video(self):

        if not stow.exists(self.video_path):
            raise Exception(f"Given video path doesn't exists {self.video_path}")

        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            raise Exception(f"Error opening video stream or file {self.video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        # width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        # height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # output_path = self.video_path.replace(f".{stow.extension(self.video_path)}", f"_{self.output_extension}.mp4")
        # out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'MP4V'), fps, (width, height))

        for framesnum in tqdm(range(frames)):
            true, frame = cap.read()
            if not true:
                break
            
            
            if self.check_video_frames_amount_correct(framesnum):
                # out.write(frame)
                if self.stop_on_end and framesnum >= self.end_video_frame:
                    break
                continue

            frame = self.custom_processing(self.flip_cv2_stream(frame))

            # out.write(frame)

            if not self.display_cv2(frame):
                break

        cap.release()
        # out.release()

    def stream_processing(self, frame):

        # Process frames using custom objects like FPSCal
        if self.custom_objects:
            for custom_object in self.custom_objects:
                frame = custom_object(frame)

        return frame

    def display_cv2(self, frame, waitTime=0):
        # Display current frame if self.show = True

        if self.show:
            event, values = self.window.read(
                timeout=waitTime, timeout_key="timeout"
            )  # get events for the window with 20ms max wait
            if event in (None, "Exit"):
                return False  # if user closed window, quit

            self.window["image"].update(
                data=cv2.imencode(".png", frame)[1].tobytes()
            )  # Update image in window
        return True

    def check_video_frames_amount_correct(self, framesnum):

        if self.end_video_frame and framesnum > self.end_video_frame:
            return True
        elif self.start_video_frame and framesnum < self.start_video_frame:
            return True

        return False

    def flip_cv2_stream(self, frame):
        # Flip given frame horizontally
        if self.flip_view_horizontal:
            return cv2.flip(frame, 1)
        elif self.flip_view_vertical:
            return cv2.flip(frame, 0)

        return frame

    def run(self):
        # Main object function to start processing image, video or webcam input
        if self.video_path != "":
            self.Engine_video()
        elif self.image_path != "":
            self.Engine_image(self.image_path)
        elif self.hikvisionip != "":
            self.Engine_hikvision()
        else:
            self.Engine_cam()
