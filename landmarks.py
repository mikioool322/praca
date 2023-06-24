from PIL import Image, ImageDraw
import face_recognition
import cv2
# Load the jpg file into a numpy array
image = face_recognition.load_image_file("stevie.jpg")

# Find all facial features in all the faces in the image
face_landmarks_list = face_recognition.face_landmarks(image)

print("I found {} face(s) in this photograph.".format(len(face_landmarks_list)))

# Create a PIL imagedraw object so we can draw on the picture
pil_image = Image.fromarray(image)
d = ImageDraw.Draw(pil_image)
print(face_landmarks_list)
for face_landmarks in face_landmarks_list:
    print(face_landmarks.keys())
    # Print the location of each facial feature in this image
    for facial_feature in face_landmarks.keys():
        print("The {} in this face has the following points: {}".format(facial_feature, face_landmarks[facial_feature]))

    # Let's trace out each facial feature in the image with a line!
    for facial_feature in face_landmarks.values():
       
        for i in facial_feature:
            print(i)
            image = cv2.circle(image, i, 8, (0, 255, 0), -1)

# Show the picture
image_rgb=cv2.cvtColor(image, cv2.COLOR_BGR2RGB) 
image_rgb = cv2.resize(image_rgb, (0, 0), fx=0.25, fy=0.25)
cv2.imshow("Punkty charakterystyczne", image_rgb)

  
# concatenate image Vertically


cv2.waitKey(0)