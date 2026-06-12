import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np
import time

#参考ページ
#https://ai.google.dev/edge/mediapipe/solutions/vision/object_detector?hl=ja

model_path = "./models/ssd_mobilenet_v2.tflite"

BaseOptions = mp.tasks.BaseOptions
ObjectDetector = mp.tasks.vision.ObjectDetector
ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = ObjectDetectorOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    max_results=5,
    score_threshold=0.35,
    category_allowlist=["cell phone"],
    running_mode=VisionRunningMode.VIDEO)

cap = cv2.VideoCapture(0)

with ObjectDetector.create_from_options(options) as detector:
    start_time = time.time()
    while cap.isOpened():
        
        scucess,frame = cap.read()
        if not scucess:
            continue
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        timestamp_ms = int(time.time() * 1000)
        result = detector.detect_for_video(mp_image, timestamp_ms)
        
        if result.detections:
            #print(result.detections)
            result_txt = "Detected cell phone"
            
        else:
            #print(result.detections)
            result_txt = "Not detected cell phone"
        
        cv2.putText(frame, text=result_txt,org=(100, 300),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1.0,color=(0, 0, 255),thickness=2,lineType=cv2.LINE_4)
        '''
            category = detection.categories[0]
            category_name = category.category_name
            socre = round(category.score,2)
            result_txt = f"object={category_name} : {socre}"
            if category_name == "cell phone":
                print("携帯電話が検出\n")
            cv2.putText(frame, text=result_txt,
            org=(100, 300+i),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0,
            color=(0, 255, 0),
            thickness=2,
            lineType=cv2.LINE_4)
            i+=30
            '''
            
        
        cv2.imshow("ObjectDetector",frame)
        
        if cv2.waitKey(5) & 0xFF == 27:
            break       

cap.release()       
cv2.destroyAllWindows()