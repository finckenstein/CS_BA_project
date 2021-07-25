import xml.etree.ElementTree as ET
import os
import shutil


def fetch_classes():
    PATH_TO_USB_FRAMES = '/home/leander/Desktop/TensorFlow/workspace/training_kitchen_tools/images/train/'
    files = os.listdir(PATH_TO_USB_FRAMES)
    classes = []
    occurrence = []

    for file in files:
        if '.xml' in file:
            try:
                tree = ET.parse(PATH_TO_USB_FRAMES + file)
                root = tree.getroot()
                for obj in root.findall('object'):
                    if obj[0].text not in classes:
                        classes.append(obj[0].text)
                        occurrence.append(1)
                    else:
                        i = classes.index(obj[0].text)
                        occurrence[i] += 1

            except Exception:
                pass

    dic_array = {}
    for clas, count in zip(classes, occurrence):
        dic_array[clas] = int(count * 0.1)

    return dic_array


def fetch_objects_in_file(tmp_root):
    obj_array = []
    for tmp_obj_file in tmp_root.findall('object'):
        obj_array.append(tmp_obj_file[0].text)
    return obj_array


def file_can_be_moved(file_tools, dic):
    for f_tool in file_tools:
        if dic[f_tool] <= 0:
            return False
    return True


def decrement_counter_in_dictionary(file_tools, dic):
    for f_tool in file_tools:
        dic[f_tool] = dic[f_tool] - 1


if __name__ == '__main__':
    PATH_TO_SOURCE = '/home/leander/Desktop/TensorFlow/workspace/training_kitchen_tools/images/train/'
    PATH_TO_DESTINATION = '/home/leander/Desktop/TensorFlow/workspace/training_kitchen_tools/images/test/'
    all_files = os.listdir(PATH_TO_SOURCE)

    classes_with_occurrence = fetch_classes()
    print(classes_with_occurrence)
    counter = 0
    files_to_move = []

    for file in all_files:
        if '.xml' in file:
            tree = ET.parse(PATH_TO_SOURCE + file)
            root = tree.getroot()
            tools_in_file = fetch_objects_in_file(root)
            if file_can_be_moved(tools_in_file, classes_with_occurrence):
                decrement_counter_in_dictionary(tools_in_file, classes_with_occurrence)
                file_name = file.split(".")
                img = file_name[0] + ".jpg"
                files_to_move.append((file, img))
                counter += 1
    print(classes_with_occurrence)
    print(counter)

    for file in files_to_move:
        tmp = shutil.move(PATH_TO_SOURCE + file[0], PATH_TO_DESTINATION)
        if tmp != PATH_TO_DESTINATION + file[0]:
            print("Error in moving file: ", file[0])

        tmp = shutil.move(PATH_TO_SOURCE + file[1], PATH_TO_DESTINATION)
        if tmp != PATH_TO_DESTINATION + file[1]:
            print("Error in moving file: ", file[1])

    print(len(files_to_move))





