import xml.etree.ElementTree as ET
import os
import cv2
import math

# https://docs.python.org/3/library/xml.etree.elementtree.html


def find_video_id(file_name):
    tmp = file_name.split("_")
    return tmp[0]


def find_seconds(file_name):
    tmp = file_name.split("_")
    tmp_sec = tmp[2].split(".")
    return tmp_sec[0]


def fetch_video_id(f):
    file_parts_array = f.split('_')
    tmp_id = ''

    for file_part in file_parts_array:
        if '(' in file_part:
            start_index = file_part.index('(') + 1
            while not file_part[start_index] == ')':
                tmp_id += file_part[start_index]
                start_index += 1

    return int(tmp_id)


def fetch_video_with_seconds(string_object):
    PATH_TO_FRAMES = "../../../TensorFlow/workspace/training_kitchen_tools/images/train/"
    files = os.listdir(PATH_TO_FRAMES)
    video_array = []

    for file in files:
        if '.xml' in file:
            try:
                tree = ET.parse(PATH_TO_FRAMES + file)
                # print("File is well-formed: ", file)
                root = tree.getroot()
                for child in root:
                    if child.tag == 'object':
                        for more_child in child:
                            if more_child.tag == 'name' and more_child.text == string_object:
                                video_id = find_video_id(file)
                                sec_id = find_seconds(file)
                                print(file)
                                video_array.append({int(video_id): [int(sec_id)]})
                                # if not video_in_array(video_array, video_id):
                                #     print("ADDING IF")
                                #     video_array.append({int(video_id): [int(sec_id)]})
                                # else:
                                #     print("ADDING ELSE")
                                #     append_seconds_to_video_array(video_array, video_id, sec_id)
            except Exception:
                print("FILE IS BAD: ", file)
                pass
    print(video_array)

    index = 0
    for elem in video_array:
        for key in elem:
            video_array[index][key].append(min(video_array[index][key]) - 1)
            video_array[index][key].append(max(video_array[index][key]) + 1)
            video_array[index][key].sort()
            # mini = video_array[index][key][0]-1
            # maxi = video_array[index][key][len(video_array[index][key])-1]+1
            # print(mini, maxi)
            # video_array[index][key] = list(range(mini, maxi))
        index += 1

    return video_array


def fetch_all_keys(dic_array):
    tmp = []
    for elem in dic_array:
        for key in elem:
            if key not in tmp:
                tmp.append(key)
    return tmp


def fetch_values(dic_array, video_id):
    for elem in dic_array:
        for key in elem:
            if key == video_id:
                return elem[key]


if __name__ == '__main__':
    video_with_seconds = fetch_video_with_seconds("skimmer")
    print(video_with_seconds)
    list_of_keys = fetch_all_keys(video_with_seconds)
    print(list_of_keys)

    PATH_TO_FRAMES_TO_SAVE = "../../../../Documents/skimmer/"
    PATH_TO_USB_VIDEOS = "../../../../../../media/leander/1F1C-606E/videos/"
    files = os.listdir(PATH_TO_USB_VIDEOS)

    for file in files:
        if ".mp4" in file:
            temp_vid_id = fetch_video_id(file)
            if temp_vid_id in list_of_keys:
                print(file)
                video = PATH_TO_USB_VIDEOS + file
                capture = cv2.VideoCapture(video)
                frame_rate = capture.get(5)
                seconds_id = 0
                i = 0
                while capture.isOpened():
                    frame_id = capture.get(1)  # current frame number
                    ret, frame = capture.read()
                    if not ret:
                        break

                    if frame_id % math.floor(frame_rate) == 0:
                        seconds_id += 1
                    elif seconds_id in fetch_values(video_with_seconds, temp_vid_id):
                        print("ADDING FRAME NOW")
                        filename = PATH_TO_FRAMES_TO_SAVE + "not_sec_" + str(temp_vid_id) + "_frame_" + str(i) + ".jpg"
                        cv2.imwrite(filename, frame)
                    i += 1

                capture.release()
                cv2.destroyAllWindows()