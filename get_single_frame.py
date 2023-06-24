# program to capture single image from webcam in python
  
# importing OpenCV library
import cv2
import face_recognition
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils
from PIL import Image
from time import sleep
def startcam():
    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    #video_capture = cv2.VideoCapture('faces.mp4')
    return video_capture 
 
# initialize the camera
# If you have multiple camera connected with 
# current device, assign a value in cam_port 
# variable according to that
def singleframe():
    
    
    try:
        webcam = startcam()
        ret, frame = webcam.read()
        webcam.release()
    except:
        sleep(2)

    return frame[:, :, ::-1]
def frame_to_bytes(frame):
    ret, buffer = cv2.imencode('.jpg', frame)
    
    frame = buffer.tobytes()
    
    return frame

def get_small_frame(frame):
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    return small_frame

def singleframe_rbg():
    ret, frame = startcam().read()
    cv2.waitKey(10)
    webcam.release()
    cv2.destroyAllWindows()
    return frame[:, :, ::-1]

def frame_rbg(frame):
    

    return frame[:, :, ::-1]

def is_face_on_frame(frame):
    
    face_locations = face_recognition.face_locations(frame)

    if len(face_locations) == 1:
        return 0
    elif len(face_locations) > 1:
        return 1
    else: 
        return 2

def draw_rect(frame):
    face_locations = face_recognition.face_locations(frame)
    
    if len(face_locations) > 0:
        face_cords = face_locations[0]
        
        top = face_cords[0]
        right = face_cords[1]
        bottom = face_cords[2]
        left = face_cords[3]

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
    return frame[:, :, ::-1]

def crop_face(frame):

    face_locations = face_recognition.face_locations(frame)
    if len(face_locations) > 0:
        face_cords = face_locations[0]
        
        top = face_cords[0]
        right = face_cords[1]
        bottom = face_cords[2]
        left = face_cords[3]
        print(face_locations)
        return frame[top:bottom, left:right, ::-1]
    else:
        return -1
def save_img(filename, image):
    return cv2.imwrite(filename, image)




