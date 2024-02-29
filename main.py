# Import necessary modules
from Modules.Call_Modules import FPScounter
from Modules.CameraEngine import Engine
from Modules.MediapipeFaceDetection import MediaPipeFaceDetection
from Modules.FaceNet import FaceNet
from Modules.FacialImageCapture import FacialImageCap
import Modules.CameraCredentialSystem as CameraCredentialSystem

import PySimpleGUI as sg
from multiprocessing import Process

from tkinter import Tk
from tkinter.filedialog import askopenfilename  # For Video & Image
from Modules.PasswordSystem import (
    password_save_process,
    read_json_file,
    get_credentials_for_camera,
)

# GUI layout
layout = [
    [sg.Text("Camera Name:"), sg.Input(key="custom_name")],
    [sg.Text("Webcam ID (Normally 0 or 1):"), sg.Input(key="webcam_id_num")],
    [sg.Text("Hikvision Username:"), sg.Input(key="hikvisionusr")],
    [sg.Text("Hikvision Password:"), sg.Input(key="hikvisionpwd")],
    [sg.Text("Hikvision IP:"), sg.Input(key="hikvisionip")],
    [sg.Text("Image Path:"), sg.Input(key="image_path")],
    [sg.Text("Video Path:"), sg.Input(key="video_path")],
    [
        sg.Text("Threshold:"),
        sg.Input(key="threshold"),
        sg.Button("Change", key="changethreshold"),
    ],
    [sg.Text("Show Stream:"), sg.Checkbox(" ", default=True, key="show")],
    [
        sg.Text("Flip View Horizontal:"),
        sg.Checkbox(" ", default=True, key="flip_view_horizontal"),
        sg.Text("Flip View Vertical:"),
        sg.Checkbox(" ", default=False, key="flip_view_vertical"),
    ],
    [sg.Button("Hikvision Credentials (cmd only + Depricated)")],
    [
        sg.Text("Face ID/Name:"),
        sg.Input(key="faceid"),
        sg.Button("Capture Face Image"),
        sg.Button("Refresh Image Database", key="refreshdata"),
    ],
    [sg.Text("Camera to Save:"), sg.Button("Save")],
    [
        sg.Text("Camera to Run:"),
        sg.Combo([], key="runcamdropdown", size=(50, 50)),
        sg.Button("Run"),
        sg.Button("Refresh"),
        sg.Button("Load Camera Values", key="LoadValues"),
    ],
    [sg.Button("Exit")],
]

window = sg.Window("Script Parameters", layout)

facenet = FaceNet(
    # Face face_detector Object
    face_detector=MediaPipeFaceDetection(),
    # Weights Model from TF converted using Onyx
    onnx_model="onnx models/faceNet.onnx",
    # Basically Folder with the face(s) that are used
    anchors="Faces/Process",
    # CPU or GPU
    use_cpu=False,
)

engine_instances = (
    CameraCredentialSystem.load_camera_properties()
)  # Load instances of the Engine
recent_engine_instance = Engine()

while True:
    event, values = window.read()

    if event == "Capture Face Image":
        webcam_id_num = str(values["webcam_id_num"])
        faceint = str(values["faceid"])

        FacialImageCap(faceint, webcam_id_num)

        # recent_engine_instance.detect_save_faces()

        facenet = FaceNet(
            # Face face_detector
            face_detector=MediaPipeFaceDetection(),
            # Weights Model from TF converted using Onyx
            onnx_model="onnx models/faceNet.onnx",
            # Basically Folder with the face(s) that are used
            anchors="Faces/Process",
            # CPU or GPU
            use_cpu=False,
        )

    if event == "Run":
        engine_instance = Engine(
            custom_name=values["custom_name"],
            webcam_id_num=str(values["webcam_id_num"]),
            hikvisionusr=values["hikvisionusr"],
            hikvisionpwd=values["hikvisionpwd"],
            hikvisionip=values["hikvisionip"],
            image_path=values["image_path"],
            video_path=values["video_path"],
            show=values["show"],
            flip_view_horizontal=values["flip_view_horizontal"],
            flip_view_vertical=values["flip_view_vertical"],
            custom_objects=[facenet, FPScounter()],
        )

        # Run Engine
        engine_instance.run()

    if event == "Save":
        engine_instance = Engine(
            custom_name=values["custom_name"],
            webcam_id_num=str(values["webcam_id_num"]),
            hikvisionusr=values["hikvisionusr"],
            hikvisionpwd=values["hikvisionpwd"],
            hikvisionip=values["hikvisionip"],
            image_path=values["image_path"],
            video_path=values["video_path"],
            show=values["show"],
            flip_view_horizontal=values["flip_view_horizontal"],
            flip_view_vertical=values["flip_view_vertical"],
            custom_objects=[facenet, FPScounter()],
        )

        # Add the engine instance to the list
        engine_instances.append(engine_instance)

        # Update the dropdown menu with custom names
        window["runcamdropdown"].update(
            values=[instance.custom_name for instance in engine_instances]
        )

        CameraCredentialSystem.save_camera_properties(engine_instances)
        print(engine_instances)

    if (
        event == "LoadValues"
    ):  # Add this section for loading values based on custom name
        selected_custom_name = values["runcamdropdown"]

        # Find the engine instance with the selected custom name
        selected_instance = next(
            (
                instance
                for instance in engine_instances
                if instance.custom_name == selected_custom_name
            ),
            None,
        )

        if selected_instance:
            # Update GUI input fields with values of the selected camera instance
            window["hikvisionpwd"].update(value=selected_instance.hikvisionpwd)
            window["hikvisionusr"].update(value=selected_instance.hikvisionusr)
            window["hikvisionip"].update(value=selected_instance.hikvisionip)
            window["image_path"].update(value=selected_instance.image_path)
            window["video_path"].update(value=selected_instance.video_path)
            window["webcam_id_num"].update(value=selected_instance.webcam_id_num)
            window["show"].update(value=selected_instance.show)
            window["flip_view_horizontal"].update(
                value=selected_instance.flip_view_horizontal
            )
            window["flip_view_vertical"].update(
                value=selected_instance.flip_view_vertical
            )
            window["custom_name"].update(value=selected_instance.custom_name)

    if event == "refreshdata":

        facenet = FaceNet(
            # Face face_detector
            face_detector=MediaPipeFaceDetection(),
            # Weights Model from TF converted using Onyx
            onnx_model="onnx models/faceNet.onnx",
            # Basically Folder with the face(s) that are used
            anchors="Faces/Process",
            # CPU or GPU
            use_cpu=False,
        )

        print("threshhold is:" + str(facenet.face_recognition_threshold))

    if event == "Refresh":
        # Update the dropdown menu with custom names
        window["runcamdropdown"].update(
            values=[instance.custom_name for instance in engine_instances]
        )

    if event == "changethreshold":

        threshold = (values["threshold"],)

        if threshold != None:
            facenet = FaceNet(
                # Face face_detector
                face_detector=MediaPipeFaceDetection(),
                # Weights Model from TF converted using Onyx
                onnx_model="onnx models/faceNet.onnx",
                # Basically Folder with the face(s) that are used
                anchors="Faces/Process",
                # CPU or GPU
                use_cpu=False,
                # set threshold
                face_recognition_threshold=threshold,
            )

            print("threshhold is:" + str(facenet.face_recognition_threshold))
        else:
            pass

    if event == "Hikvision Credentials (cmd only)":
        data, file_path = read_json_file()
        password_save_process(data, file_path)

    if event == sg.WINDOW_CLOSED or event == "Exit":
        break
