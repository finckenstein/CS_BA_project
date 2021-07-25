import xml.etree.ElementTree as ET
import os

# https://docs.python.org/3/library/xml.etree.elementtree.html


def file_name_is_found(image_name, all_files):
    for cur_file in all_files:
        if image_name == cur_file:
            return True
    return False


if __name__ == '__main__':
    folder_name = "test"
    PATH_TO_SOURCE = '/home/leander/Desktop/TensorFlow/workspace/training_kitchen_tools/images/'+folder_name+'/'
    files = os.listdir(PATH_TO_SOURCE)
    classes = []
    occurrence = []
    bad_path = 0
    bad_folder = 0
    bad_file = 0
    bad_width = 0
    bad_height = 0
    silicone = 0
    updated_annotation = 0
    bad_file_name = 0

    for file in files:
        if '.xml' in file:
            try:
                tree = ET.parse(PATH_TO_SOURCE + file)
                root = tree.getroot()
                if root.get('verified') is None:
                    root.set('verified', 'yes')
                    tree.write(PATH_TO_SOURCE + file)
                    updated_annotation += 1
                for child in root:
                    if child.tag == 'path' and not (PATH_TO_SOURCE in child.text):
                        tmp_file = file.split(".")
                        child.text = PATH_TO_SOURCE + tmp_file[0] + ".jpg"
                        tree.write(PATH_TO_SOURCE + file)
                        print(file)
                        bad_path += 1
                    elif child.tag == 'folder' and not child.text == folder_name:
                        child.text = folder_name
                        tree.write(PATH_TO_SOURCE + file)
                        bad_folder += 1
                    elif child.tag == 'size':
                        for more_child in child:
                            if more_child.tag == 'width' and not more_child.text == '640':
                                bad_width += 1
                            elif more_child.tag == 'height' and not more_child.text == '640':
                                bad_height += 1
                    elif child.tag == 'filename' and not file_name_is_found(child.text, files):
                        print(file)
                        image_name = child.text.split(".")
                        child.text = image_name[0] + ".jpg"
                        tree.write(PATH_TO_SOURCE + file)
                        bad_file_name += 1

            except Exception:
                bad_file += 1
                print("FILE IS BAD: ", file)
                pass

    print("BAD FILES: ", bad_file)
    print("BAD PATHS: ", bad_path)
    print("BAD FOLDER: ", bad_folder)
    print("BAD HEIGHT: ", bad_height)
    print("BAD WIDTH: ", bad_width)
    print("BAD SILICONE: ", silicone)
    print("UPDATED ANNOTATION: ", updated_annotation)
    print("BAD FILENAME: ", bad_file_name)


# if child.tag == 'path' and not "/home/leander/Desktop/TensorFlow/workspace/training_kitchen_tools/images/train/" in child.text:
#     tmp_file = file.split(".")
#     child.text = "/home/leander/Desktop/TensorFlow/workspace/training_kitchen_tools/images/train/" + tmp_file[
#         0] + ".jpg"
#     print("/home/leander/Desktop/TensorFlow/workspace/training_kitchen_tools/images/train/" + tmp_file[0] + ".jpg")
#     tree.write(PATH_TO_USB_FRAMES + file)
# elif child.tag == 'folder' and not child.text == 'train':
#     file_counter += 1
#     child.text = "train"
#     tree.write(PATH_TO_USB_FRAMES + file)

