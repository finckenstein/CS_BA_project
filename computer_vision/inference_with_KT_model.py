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
import cv2

from computer_vision.tensorflow_object_detection_utils import ops as utils_ops
from computer_vision.tensorflow_object_detection_utils import visualization_utils as vis_util


def run_inference_for_single_image(model, image):
    image = np.asarray(image)
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    # Run inference
    model_fn = model.signatures['serving_default']
    output_dict = model_fn(input_tensor)

    # print(output_dict['detection_classes'])

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


def make_inference(category_index, image_np, model):
    # Actual detection.
    output_dict = run_inference_for_single_image(model, image_np)
    # Visualization of the results of a detection.
    return vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        instance_masks=output_dict.get('detection_masks_reframed', None),
        use_normalized_coordinates=True,
        line_thickness=8,
        min_score_thresh=0.2)


def select_detected_kitchenware(tools_detected):
    detectable_kitcheware = ["pot", "pan", "bowl", "baking-sheet"]
    if not tools_detected:
        print("[select_detected_kitchenware] return []")
        return []
    max_value = (None, 0)
    for object in tools_detected:
        obj_array = object.split(": ")
        percentage_str = obj_array[1]
        score = int(percentage_str[:-1])
        if obj_array[0] in detectable_kitcheware and max_value[1] < score:
            max_value = (obj_array[0], score)
    # print("[select_detected_kitchenware] return: ", max_value[0], " with probability: ", max_value[1])
    return max_value[0]


# the function will only ever make a inference for one second
def iterate_over_video(path_to_video, timestamp, category_index, detection_model):
    utils_ops.tf = tf.compat.v1
    tf.gfile = tf.io.gfile

    cap = cv2.VideoCapture(path_to_video)
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp*1000)
    most_probable_kitchenware = None

    while cap.isOpened():
        ret, image_np = cap.read()
        if not ret:
            # print("\n[make_inference] returning FALSE\n")
            return None

        kitchenware_detected = make_inference(category_index, image_np, detection_model)
        most_probable_kitchenware = select_detected_kitchenware(kitchenware_detected)
        # print("[iterate_over_video] most probable kitchenware detected: ", most_probable_kitchenware)

        cv2.imshow('object_detection', cv2.resize(image_np, (640, 640)))

        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
        break

    # print("\nCAP RELEASED AND DESTROYED\n")
    cap.release()
    cv2.destroyAllWindows()
    return most_probable_kitchenware
