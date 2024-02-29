import cv2
import stow
import typing
import numpy
import onnxruntime
import random


class FaceNet:
    def __init__(
        self,
        face_detector: object,
        onnx_model: str = "onnx models/faceNet.onnx",
        anchors: typing.Union[str, dict] = "Faces/Process",
        use_cpu: bool = False,
        face_recognition_threshold: float = 0.45,
        color: tuple = (51, 204, 255),
        thickness: int = 2,
    ):

        # zorg voor dat self dezelfde values heeft
        self.face_detector = face_detector
        self.face_recognition_threshold = face_recognition_threshold
        self.thickness = thickness
        self.color = color

        if bool(stow.exists(onnx_model)) != True:
            raise Exception(f"Model doesn't exists in {onnx_model}")

        onnxproviders = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        onnxproviders = (
            onnxproviders
            if onnxruntime.get_device() == "GPU" and not use_cpu
            else onnxproviders[::-1]
        )

        self.onnx_session = onnxruntime.InferenceSession(
            onnx_model, providers=onnxproviders
        )
        self.input_shape = self.onnx_session._inputs_meta[0].shape[1:3]
        self.anchors = (
            self.load_anchors(anchors) if isinstance(anchors, str) else anchors
        )

    def normalize(self, img):
        # Normalize foto's (basically strech)
        mean, std = img.mean(), img.std()
        return (img - mean) / std

    def l2_normalize(self, x, axis: int = -1, epsilon: float = 1e-10):
        output = x / numpy.sqrt(
            numpy.maximum(numpy.sum(numpy.square(x), axis=axis, keepdims=True), epsilon)
        )
        return output

    def detect_save_faces(self, image, output_dir: str = "faces"):
        face_crops = [
            image[t:b, l:r]
            for t, l, b, r in self.face_detector(image, return_tlbr=True)
        ]

        if face_crops == []:
            return False

        stow.mkdir(output_dir)

        for index, crop in enumerate(face_crops):
            output_path = stow.join(output_dir, f"face_{str(index)}.png")
            cv2.imwrite(output_path, crop)
            print("Crop saved to:", output_path)

        self.anchors = self.load_anchors(output_dir)

        return True

    def cosinus_compare(self, a, b: typing.Union[numpy.ndarray, list]):

        if isinstance(a, list):
            a = numpy.array(a)

        if isinstance(b, list):
            b = numpy.array(b)

        print(numpy.dot(a, b.T) / (numpy.linalg.norm(a) * numpy.linalg.norm(b)))

        return numpy.dot(a, b.T) / (numpy.linalg.norm(a) * numpy.linalg.norm(b))

    def draw(self, image, face_crops: dict):

        # Draw face crops on image
        for value in face_crops.values():
            t, l, b, r = value["tlbr"]
            cv2.rectangle(image, (l, t), (r, b), self.color, self.thickness)
            cv2.putText(
                image,
                stow.name(value["name"]),
                (l, t - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                self.color,
                self.thickness,
            )

        return image

    def load_anchors(self, faces_path):

        # Generate ankers for given path of face image folder

        anchors = {}
        if not stow.exists(faces_path):
            return {}

        for face_path in stow.ls(faces_path):
            anchors[stow.basename(face_path)] = self.encode(cv2.imread(face_path.path))

        return anchors

    def encode(self, face_image):

        # Encode face image with FaceNet model
        face = self.normalize(face_image)
        face = cv2.resize(face, self.input_shape).astype(numpy.float32)

        encode = self.onnx_session.run(
            None,
            {self.onnx_session._inputs_meta[0].name: numpy.expand_dims(face, axis=0)},
        )[0][0]
        normalized_encode = self.l2_normalize(encode)

        return normalized_encode

    def __call__(self, frame):

        # print("Call FaceNet")
        # Face recognition pipeline

        # face_crops = {index: {"name": "Unknown", "tlbr": tlbr} for index, tlbr in enumerate(self.face_detector(frame, return_tlbr=True))}
        # cool unknown variable
        face_crops = {
            index: {
                "name": "SystemID" + str(round(random.uniform(0, 100), 1)),
                "tlbr": tlbr,
            }
            for index, tlbr in enumerate(self.face_detector(frame, return_tlbr=True))
        }

        for key, value in face_crops.items():
            t, l, b, r = value["tlbr"]
            face_encoding = self.encode(frame[t:b, l:r])
            difference = self.cosinus_compare(
                face_encoding, list(self.anchors.values())
            )

            if numpy.max(difference) > float(self.face_recognition_threshold):
                face_crops[key]["name"] = list(self.anchors.keys())[
                    numpy.argmax(difference)
                ]

        frame = self.draw(frame, face_crops)

        return frame
