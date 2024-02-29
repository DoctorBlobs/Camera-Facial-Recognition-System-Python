import cv2
import pathlib as pl
import numpy
import typing
import os
import mediapipe

def face_recognition(webcam, face_id, imgpath):
    
    face_cascade = cv2.CascadeClassifier('Cascade/data/haarcascade_frontalface_alt.xml')
    cap = cv2.VideoCapture(int(webcam))
    
    count = 0
    
    while(True):
        
        files = os.listdir(imgpath)
        
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(frame, scaleFactor=1.5, minNeighbors=5, minSize=(30, 30))
                
        for(x, y, w, h) in faces:
            print(x, y, w, h)
            roi_gray = gray[y:y+h, x:x+w] #Save gray image cut of the face
            roi_color = frame[y:y+h, x:x+w] #Save color image of face using coordinates
            
            count += 1
                        
            rectcolor = (255,0,0) #BGR
            stroke = 2
            end_x = x + w
            end_y = y + h
            cv2.rectangle(frame, (x,y), (end_x, end_y), rectcolor, 1)
            cv2.imwrite(imgpath + str(face_id) + '-' + str(count) + ".jpg", frame[y:y+h,x:x+w])
            
            cv2.imshow('image', roi_color)

            print("Folder '{imgpath}' is full.")
            cap.release()
            cv2.destroyAllWindows()
            return

        if cv2.waitKey(20) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()     
            break     

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")

def FacialImageCap(faceid, webcamid):
    # max_files_allowed = 1
    
    face_id = faceid
    webcam = webcamid
    
    folder_path = "D:/Coding/Languages/Python/Projects/FaceRecognition/faces/"  # Change this to the desired folder name

    # create_folder_if_not_exists(folder_path)
    face_recognition(webcam, face_id, folder_path)