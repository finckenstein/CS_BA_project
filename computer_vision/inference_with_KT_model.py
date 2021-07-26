#!/usr/bin/env python
# coding: utf-8

# '%pip install -U --pre tensorflow=="2.*"'
# '%pip install tf_slim'
# '%pip install pycocotools'

# if "models" in pathlib.Path.cwd().parts:
#     while "models" in pathlib.Path.cwd().parts:
#         os.chdir('..')

# '%cd models/research/\nprotoc object_detection/protos/*.proto --python_out=.'
# '%cd models/research\npip install .'
import math

import numpy as np
import tensorflow as tf

import pathlib
import cv2
import os

from computer_vision.tensorflow_object_detection_utils import ops as utils_ops
from computer_vision.tensorflow_object_detection_utils import label_map_util
from computer_vision.tensorflow_object_detection_utils import visualization_utils as vis_util


def load_model(model_path):
    model_dir = pathlib.Path(model_path) / "saved_model"
    model = tf.saved_model.load(str(model_dir))
    return model


def run_inference_for_single_image(model, image):
    image = np.asarray(image)
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    # Run inference
    model_fn = model.signatures['serving_default']
    output_dict = model_fn(input_tensor)

    print(output_dict['detection_classes'])

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    # Handle models with masks:
    if 'detection_masks' in output_dict:
        # Reframe the the bbox mask to the image size.
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            output_dict['detection_masks'], output_dict['detection_boxes'],
            image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
                                           tf.uint8)
        output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()

    return output_dict


def make_inference(category_index, capture, model, frame_rate):
    frame_id = capture.get(1)  # current frame number
    ret, image_np = capture.read()
    if not ret:
        print("\n[make_inference] returning FALSE\n")
        return False

    if frame_id % math.floor(frame_rate) == 0:
        return False

    # Actual detection.
    output_dict = run_inference_for_single_image(model, image_np)
    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        instance_masks=output_dict.get('detection_masks_reframed', None),
        use_normalized_coordinates=True,
        line_thickness=8,
        min_score_thresh=0.40)

    cv2.imshow('object_detection', cv2.resize(image_np, (640, 640)))

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
    print("\n[make_inference] returning TRUE\n")
    return True


def iterate_over_video(path_to_video, seconds_into_video):
    utils_ops.tf = tf.compat.v1
    tf.gfile = tf.io.gfile

    PATH_TO_LABELS = '/home/leander/Desktop/automatic_KB/computer_vision/CV_Kitchen_Tools/kitchen_tools_label_map.pbtxt'
    category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

    model_name = '/home/leander/Desktop/automatic_KB/computer_vision/CV_Kitchen_Tools/CV_KT_detection_model_B4/'
    detection_model = load_model(model_name)

    # print("\n\n\nHELLO: ", detection_model.signatures['serving_default'].inputs, "\n")

    cap = cv2.VideoCapture(path_to_video)
    frame_rate = cap.get(5)
    sec_counter = 0

    while cap.isOpened():
        frame_id = cap.get(1)  # current frame number
        ret, image_np = cap.read()
        if not ret:
            print("\n[make_inference] returning FALSE\n")
            return False

        if frame_id % math.floor(frame_rate) == 0:
            sec_counter += 1
        elif sec_counter >= seconds_into_video:
            if not make_inference(category_index, cap, detection_model, frame_rate):
                break

    print("\nCAP RELEASED AND DESTROYED\n")
    cap.release()
    cv2.destroyAllWindows()
