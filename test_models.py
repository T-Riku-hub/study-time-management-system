#https://qiita.com/Pokemon_Jet-787/items/a6678c228b7f5bf8d211

from ultralytics import YOLO
import cv2
import time
model = YOLO("./models/best_int8.tflite")
result_text=""
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()

    results = model(frame,verbose=False,save=False,conf=0.5)
    
    boxes = results[0].boxes

    if len(boxes) == 0:
        print("スマートフォンは検知されていない")
        result_text="Not detected smartphone"
    else:
        print("スマートフォンを検知")
        result_text="Detected smartphone"
    
            
    annotated = results[0].plot()
    cv2.putText(annotated, text=result_text,org=(100, 300),
    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
    fontScale=1.0,
    color=(0, 0, 255),
    thickness=2,
    lineType=cv2.LINE_4)
    
    cv2.imshow("result", annotated)

    if cv2.waitKey(1) == 27:
        break
cap.release()
cv2.destroyAllWindows()