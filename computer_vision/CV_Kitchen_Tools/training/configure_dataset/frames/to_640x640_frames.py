from PIL import Image
import os

if __name__ == '__main__':
    PATH_TO_USB_FRAMES = "../../../../Documents/skimmer/"
    PATH_TO_RESIZED_FRAMES = "../../../../Documents/skimmer_resized/"
    images = os.listdir(PATH_TO_USB_FRAMES)

    size = 640, 640

    for image in images:
        try:
            image_and_extension = image.split(".")
            im = Image.open(PATH_TO_USB_FRAMES+image)
            im = im.resize(size, Image.HAMMING)
            im.save(PATH_TO_RESIZED_FRAMES+image_and_extension[0]+".jpg", quality=100)
            print(im.size)
        except IOError:
            print("failed to open: " + image)

