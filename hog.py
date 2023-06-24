import face_recognition
from PIL import Image, ImageDraw
import numpy as np
from skimage.feature import hog
from skimage import exposure
import cv2



def create_HOG_image(image):
    fd, hog_image = hog(image, orientations=8, pixels_per_cell=(8, 8),
                            cells_per_block=(1, 1), visualize=True, multichannel=True)

    # Rescale histogram for better display
    hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(1, 15))

    return hog_image_rescaled

def detect_mark_faces(image, hog_image):
    boxes = face_recognition.face_locations(image, model='hog')
    for (top, right, bottom, left) in boxes:
        # draw the predicted face name on the image
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.rectangle(hog_image, (left, top), (right, bottom), (255, 255, 0), 2)

image = cv2.imread("usain.jpg")
#image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
hog_image = create_HOG_image(image)
#detect_mark_faces(image,hog_image)
cv2.imshow("Wejsciowy", image)
cv2.imshow("Wynikowy", hog_image)

  
# concatenate image Vertically


cv2.waitKey(0)