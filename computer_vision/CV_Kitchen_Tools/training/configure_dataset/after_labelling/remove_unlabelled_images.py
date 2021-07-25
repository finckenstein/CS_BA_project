import os


def image_is_annotated(file_directory, index):
    current_image = file_directory[index].split(".")
    for tmp_file in file_directory:
        if ".xml" in tmp_file:
            xml_file = tmp_file.split(".")
            if xml_file[0] == current_image[0]:
                return True
    return False


if __name__ == '__main__':
    PATH_TO_RESIZED_FRAMES = '/home/leander/Desktop/TensorFlow/workspace/training_kitchen_tools/images/test/'
    files = os.listdir(PATH_TO_RESIZED_FRAMES)
    i = 0
    not_annotated_counter = 0

    while i < len(files):
        if ".jpg" in files[i] and not image_is_annotated(files, i):
            print(files[i])
            # os.remove(PATH_TO_RESIZED_FRAMES + files[i])
            not_annotated_counter += 1
        i += 1
    print(not_annotated_counter)