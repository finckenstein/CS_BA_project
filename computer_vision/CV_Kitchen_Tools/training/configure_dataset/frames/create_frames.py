import cv2
import math
import os


def fetch_video_id(f):
    file_parts_array = f.split('_')
    tmp_id = ''

    for file_part in file_parts_array:
        if '(' in file_part:
            start_index = file_part.index('(') + 1
            while not file_part[start_index] == ')':
                tmp_id += file_part[start_index]
                start_index += 1
    print(tmp_id)
    return tmp_id


if __name__ == '__main__':
    PATH_TO_USB_FRAMES = "../../../../Documents/pizza-cutter/"
    PATH_TO_USB_VIDEOS = "../../../../Documents/videos/"
    files = os.listdir(PATH_TO_USB_VIDEOS)

    for file in files:
        if ".mp4" in file:
            temp_vid_id = fetch_video_id(file)
            if temp_vid_id == 0:
                print(file)
                video = PATH_TO_USB_VIDEOS + file
                capture = cv2.VideoCapture(video)
                frame_rate = capture.get(5)
                video_id = 0

                while capture.isOpened():
                    frame_id = capture.get(1)  # current frame number
                    print(frame_id)
                    ret, frame = capture.read()
                    if not ret:
                        break

                    if frame_id % math.floor(frame_rate) == 0:
                        print("ADDING FRAME NOW")
                        filename = PATH_TO_USB_FRAMES + "not_sec_" + str(temp_vid_id) + "_frame_" + str(video_id) + ".jpg"
                        video_id += 1
                        cv2.imwrite(filename, frame)

                capture.release()
                cv2.destroyAllWindows()
