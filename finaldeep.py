import tensorflow as tf
from tensorflow import keras
import numpy as np
import pandas as pd
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import cv2
import mediapipe as mp
import serial


model = load_model('mask_detector.model')
print("[INFO] loading face detector model...")

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=.1)
ser.flush()

prev=0
trig=0
st=1

while True:
  inp1=ser.readline()[:-2]
  if st==1:
      ser.flush()
      inp1=ser.readline()[:-2]
      st=0
  inp=inp1.decode('utf-8')
  data=inp.split(':')
  if(data[0]=='Trig'):
      trig=data[1]
  if(data[0]=='Mask'):
      print("Mask:",data[1])
  if(trig=='0'):
      prev=0
  if((trig=='1' and prev==0)):
      webcam = cv2.VideoCapture(0) 
      print("Triggered")
      with mp_face_detection.FaceDetection(
        model_selection=1, min_detection_confidence=0.5) as face_detection:
        res,image=webcam.read()
        if res:
          # Convert the BGR image to RGB and process it with MediaPipe Face Detection.
          results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
      
          # Draw face detections of each face.
          if results.detections:
            
            annotated_image = image.copy()
            for detection in results.detections:
              box=detection.location_data.relative_bounding_box
              xs=round(box.xmin*image.shape[1])
              ys=round(box.ymin*image.shape[0])
              w=round(box.width*image.shape[1])
              h=round(box.height*image.shape[0])
              mp_drawing.draw_detection(annotated_image, detection)
              cv2.imshow('Anno',annotated_image)
              x=xs
              y=ys
              face_img = image[y:y+h, x:x+w]
              face = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
              face = cv2.resize(face, (224, 224))
              face = img_to_array(face)
              face = preprocess_input(face)
              face = np.expand_dims(face, axis=0)
              (mask, withoutMask) = model.predict(face)[0]
              label = "Mask" if mask > withoutMask else "No Mask"
              label2= label
              color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
              label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
              cv2.putText(image, label, (xs, ys - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
              cv2.rectangle(image, (xs, ys), (xs+w, ys+h), color, 2)
              if(label2=="No Mask"):
                      print("NO MASK DETECTED")
                      ser.write(bytes('0','utf-8'))
              else:
                   print("MASK DETECTED")
                   ser.write(bytes('1','utf-8'))
              cv2.imshow('im',image)
              cv2.waitKey(1000)
              prev=1
              webcam.release()