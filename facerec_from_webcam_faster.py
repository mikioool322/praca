from __future__ import print_function
import sys
import face_recognition
import cv2
import numpy as np
import json
import threading
import time
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils


# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)


def facerec():
    #video_capture = WebcamVideoStream(src=0).start()
    #video_capture = WebcamVideoStream(src=0).start()
    video_capture = cv2.VideoCapture(0)
    
    ##video_capture.set(4, 480)
    video_capture.set(cv2.CAP_PROP_FPS, 24)
    # res 720x480
    
    # fps > 30
    
    
    

    # Create arrays of known face encodings and their names

    known_face_encodings = [    
    ]
    known_face_names = [    
    ]

    f = open('known_faces.json', 'r+')
    load_json = json.load(f)
    faces = load_json['known_faces']
    for i in faces:
        known_face_names.append(i['name'])
        known_face_encodings.append(i['encoding'])
        
        
   
    f.close()
                     

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    is_generated = True
    frame_count = 0
    i = 0
    lock = threading.Lock()
    

    while True:
        
            print('-----------------------LOOP: ',i,'---------------------------------------')
            
            # Grab a single frame of video
        
            
            ret, frame = video_capture.read()
            
            
            
            
        
                
            # Only process every other frame of video to save time
            if process_this_frame:
                #print(i)
                # Resize frame of viyydeo to 1/4 size for faster face recognition processing
                
                start_time = time.time()
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                end = time.time()
                print(end-start_time,'---RESIZE TIME')
                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                start_time = time.time()
                rgb_small_frame = small_frame[:, :, ::-1]
                end = time.time()
                print(end-start_time,'---COLOR CONVERT TIME')
                # Find all the faces and face encodings in the current frame of video

                start_time = time.time()
                face_locations = face_recognition.face_locations(rgb_small_frame)
                end = time.time()
                print(end-start_time,'---face locations TIME')
                start_time = time.time()
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                end = time.time()
                print(end-start_time,'--- face endcodings TIME')
                face_names = []
                
                for face_encoding in face_encodings:
                    start_time = time.time()
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"
                    end = time.time()
                    print(end-start_time,'---get face matches TIME')
                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    start_time = time.time()
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                    face_names.append(name)
                    end = time.time()
                    print(end-start_time,'---get face distances TIME')
            
                
            
            process_this_frame = not process_this_frame


            # Display the results
            
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                start_time = time.time()
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                end = time.time()
                print(end-start_time,'---for loop and x TIME')
                # Draw a box around the face
                start_time = time.time()
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                end = time.time()
                print(end-start_time,'---draw rectangle TIME')
                # Draw a label with a name below the face
                start_time = time.time()
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                end = time.time()
                print(end-start_time,'---draw label TIME')
            
            # Display the resulting image
            #cv2.imshow('Video', frame)
        
            start_time = time.time()
            ret, buffer = cv2.imencode('.jpg', frame)
            end = time.time()
            print(end-start_time,'---encoding image TIME')
            
            start_time = time.time()
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(buffer) + b'\r\n')
            end = time.time()
            i+=1
            print(end-start_time,'---yield image TIME')
        
                
            
    #print(i)

    # Release handle to the webcam
    print("elo")
    video_capture.stop()
    cv2.destroyAllWindows()

    
    # dodac twarz w czsie rzeczywistym - done
    # ile twarzy maksymalnie na obrazie moze byc - 3
    # co opisuje punkt w tablicy czy kolor czy odlegosc czy kontrats itp - 68 punktów, oznaczają połozenie częsci twarzy np
    # wysokosc oczu, krawedzie nosa itp
    # 128 punktow - kodowanie tych 68 punktow
    # jaka odległosc twarzy od kamery musi byc - ??
    

    # 07.08.2022 11 godzina 
    # dodaj twarz prosto z kamerki

    # 21.08 2022 11 godzina\
    # dlaczego muli
    # liczba klatek 
    # rozdzielczosc kamerki
