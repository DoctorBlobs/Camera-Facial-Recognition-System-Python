# Import necessary modules
from Modules.Call_Modules import FPScounter
from Modules.CameraEngine import Engine
from Modules.MediapipeFaceDetection import MediaPipeFaceDetection
from Modules.FaceNet import FaceNet

import os
import json


# Initialize facenet outside the loop
facenet = FaceNet(
    # Face face_detector
    face_detector=MediaPipeFaceDetection(),
    # Weights Model from TF converted using Onyx
    onnx_model="onnx models/faceNet.onnx",
    # Basically Folder with the face(s) that are used
    anchors = 'Faces/Process',
    # CPU or GPU
    use_cpu=False,
)

def load_camera_properties(engine_filename="UserInfo/camera_properties.json"):
    try:       
        if os.stat(engine_filename).st_size == 0:
                    with open(engine_filename, "w") as engine_file:
                        json.dump([], engine_file)
        
        with open(engine_filename, "r") as engine_file:
            serialized_instances = json.load(engine_file)
            
        loaded_instances = []

        for serialized_instance in serialized_instances:
            # Get custom_name from serialized_instance or set a default value
            custom_name = serialized_instance.get('custom_name', f'Camera {len(loaded_instances) + 1}')

            # Create a dictionary containing all the attributes
            engine_attributes = {
                'hikvisionpwd': serialized_instance.get('hikvisionpwd', ''),
                'hikvisionusr': serialized_instance.get('hikvisionusr', ''),
                'hikvisionip': serialized_instance.get('hikvisionip', ''),
                'image_path': serialized_instance.get('image_path', ''),
                'video_path': serialized_instance.get('video_path', ''),
                'webcam_id_num': str(serialized_instance.get('webcam_id_num', '')),
                'show': serialized_instance.get('show', False),
                'flip_view_horizontal': serialized_instance.get('flip_view_horizontal', False),
                'flip_view_vertical': serialized_instance.get('flip_view_vertical', False),
                'custom_name': custom_name,  # Load custom name
                'custom_objects': [facenet, FPScounter()],
            }

            loaded_instance = Engine(**engine_attributes)  # Use unpacking to pass parameters

            loaded_instances.append(loaded_instance)

        return loaded_instances

    except FileNotFoundError:
        return []
        print("file not found")

def save_camera_properties(engine_instances, filename="UserInfo/camera_properties.json"):
    serialized_instances = []

    for instance in engine_instances:
        # Create a dictionary containing all the attributes including custom_name
        serialized_instance = {
            "hikvisionpwd": instance.hikvisionpwd,
            "hikvisionusr": instance.hikvisionusr,
            "hikvisionip": instance.hikvisionip,
            "image_path": instance.image_path,
            "video_path": instance.video_path,
            "webcam_id_num": instance.webcam_id_num,
            "custom_name": instance.custom_name,
            "show": instance.show,
            "flip_view_horizontal": bool(getattr(instance, 'flip_view_horizontal', False)),
            "flip_view_vertical": bool(getattr(instance, 'flip_view_vertical', False)),
        }

        serialized_instances.append(serialized_instance)

    with open(filename, "w") as file:
        json.dump(serialized_instances, file)