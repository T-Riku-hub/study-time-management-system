import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np
import time
from datetime import datetime
from ultralytics import YOLO


def calculate_eye_ratio(eye_landmarks):
    v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
    h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
    ear = (v1 + v2) / (2.0 * h) if h > 0 else 0
    return ear

model_path_landmarker = "./models/face_landmarker.task"

BaseOptions = python.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

#検出器のオプションを指定
FaceLandmarkerOptions = vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path_landmarker),
    output_face_blendshapes=False,
    running_mode=VisionRunningMode.VIDEO,
    num_faces=1
)

landmarker = vision.FaceLandmarker.create_from_options(FaceLandmarkerOptions) 

#スマートフォン検出を行うモデル
model = YOLO("./models/best_int8.tflite")

cap = cv2.VideoCapture(0)
left_indices = [33, 160, 158, 133, 153, 144]
right_indices = [362, 385, 387, 263, 373, 380]
sleep_start_time=0

try:
    while cap.isOpened():
        
        scucess,frame = cap.read()
        if not scucess:
            continue
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        timestamp_ms = int(time.time() * 1000)
        #videoの場合はmsに変換したフレームのタイムスタンプも指定する。
        detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)

        if detection_result.face_landmarks:
            height, width = frame.shape[:2]
            
            for face_idx, face_landmarks in enumerate(detection_result.face_landmarks):
                
                # ランドマーク配列作成
                landmarks_array = np.array([
                    (lm.x * width, lm.y * height)
                    for lm in face_landmarks
                ])
                
                # 目のランドマーク取得
                left_eye_points = landmarks_array[left_indices]
                right_eye_points = landmarks_array[right_indices]
                
                left_ear = calculate_eye_ratio(left_eye_points)
                right_ear = calculate_eye_ratio(right_eye_points)
                
                #(13)両目のEARの値が0.2を下回った時の処理
                if left_ear <0.2 and right_ear < 0.2:
                    if sleep_start_time == 0:
                        sleep_start_time = time.time()
                    elapsed_time = time.time()-sleep_start_time
                    if elapsed_time > 3:#10秒間両目が閉じていたら is_sleeping をTrueにする
                        print("Sleeping")
                        is_sleeping=True
                    cv2.putText(frame, f"EAR_L: {left_ear:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                        
                    cv2.putText(frame, f"EAR_R: {right_ear:.2f}", (190, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                    
                    cv2.imshow('frame', frame)
                else:
                    sleep_start_time = 0  # 目が開いたらリセット
                    results = model(frame,verbose=False,save=False,conf=0.5)
                    for result in results:
                            boxes = result.boxes
                            #スマートフォンを検出
                            if len(boxes)>=1:
                                print("スマートフォンを検出")
                                break
                    annotated = results[0].plot()
                    
                    
                    cv2.putText(annotated, f"EAR_L: {left_ear:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                        
                    cv2.putText(annotated, f"EAR_R: {right_ear:.2f}", (190, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                    
                    cv2.imshow('frame', annotated)
        if cv2.waitKey(5) & 0xFF == 27:
            break        
        time.sleep(0.05)
        
except KeyboardInterrupt:
    pass
finally:
    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()
    

#write_csv_test(now = datetime.now())
#plot_CSVFile_test()