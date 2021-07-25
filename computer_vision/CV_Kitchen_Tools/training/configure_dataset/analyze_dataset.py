import xml.etree.ElementTree as ET
import os

# https://docs.python.org/3/library/xml.etree.elementtree.html

if __name__ == '__main__':
    PATH_TO_USB_FRAMES = '/home/leander/Desktop/TensorFlow/workspace/training_kitchen_tools/images/test/'
    files = os.listdir(PATH_TO_USB_FRAMES)
    classes = []
    occurrence = []
    file_counter = 0
    label_counter = 0
    bad_file = 0

    for file in files:
        if '.xml' in file:
            try:
                tree = ET.parse(PATH_TO_USB_FRAMES + file)
                file_counter += 1
                # print("File is well-formed: ", file)
                root = tree.getroot()
                for child in root:
                    if child.tag == 'object':
                        for more_child in child:
                            if more_child.tag == 'name':
                                label_counter += 1
                                if more_child.text not in classes:
                                    classes.append(more_child.text)
                                    occurrence.append(1)
                                else:
                                    i = classes.index(more_child.text)
                                    occurrence[i] += 1
            except Exception:
                bad_file += 1
                print("FILE IS BAD: ", file)
                pass

    print("GOOD FILES: ", file_counter)
    print("BAD FILES: ", bad_file)
    print("TOTAL LABELS: ", label_counter)

    dic_array = {}
    for clas, count in zip(classes, occurrence):
        dic_array[clas] = count

    sorted_dic = sorted(dic_array.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    i = 1
    for elem in sorted_dic:
        # if int(elem[1]) < 400:
            print(i, elem)
            i += 1
