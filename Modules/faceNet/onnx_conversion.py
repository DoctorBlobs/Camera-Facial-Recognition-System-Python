import tensorflow as tf
import tf2onnx
from TensorflowArchitecture import ResNetV1

def conversion():
    facenet_weights_path = "models/facenet_keras_weights.h5"
    onnx_model_output_path = "models/faceNet.onnx"

    faceNet = ResNetV1()
    faceNet.load_weights(facenet_weights_path) 

    spec = (tf.TensorSpec(faceNet.inputs[0].shape, tf.float32, name="image_input"),)
    tf2onnx.convert.from_keras(faceNet, output_path=onnx_model_output_path, input_signature=spec)\

conversion()