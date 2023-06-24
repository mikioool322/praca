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



image =  cv2.imread('usain.jpg')
#image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
hog_image = create_HOG_image(image)


  
# concatenate image Vertically


image1 = Image.open("usain.jpg")
image2 = hog_image

# Ustalenie wysokości białego pola
title_height = 50

# Utworzenie nowego obrazu z połączonymi obrazkami
merged_image = Image.new("RGB", (max(image1.width, image2.width), image1.height + image2.height + title_height), (255, 255, 255))

# Wklejenie pierwszego obrazka
merged_image.paste(image1, (0, title_height))

# Wklejenie drugiego obrazka
merged_image.paste(image2, (0, image1.height + title_height))

# Dodanie tytułu na górze
draw = ImageDraw.Draw(merged_image)
font = ImageFont.truetype("arial.ttf", 20)
title_text = "Porównanie dwóch obrazków"
text_width, text_height = draw.textsize(title_text, font=font)
text_position = ((merged_image.width - text_width) // 2, (title_height - text_height) // 2)
draw.text(text_position, title_text, fill=(0, 0, 0), font=font)

# Wyświetlenie obrazu z dwoma obrazkami
merged_image.show()