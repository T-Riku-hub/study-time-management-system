import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np
import time
import gpiozero

#使用するグローバル変数を初期化
is_finish = False
is_sleeping = False
is_detect_cell_phone=False

#EARを計算する関数
def calculate_eye_ratio(eye_landmarks):
    v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
    h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
    ear = (v1 + v2) / (2.0 * h) if h > 0 else 0
    return ear

def detect_sleep_and_cell_phone():
    
    global is_finish
    global is_sleeping
    global is_detect_cell_phone
    
    #モデルのパスを指定
    model_path = "./models/face_landmarker.task"

    BaseOptions = python.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    #検出器(Face Landmarker)のオプションを設定
    FaceLandmarkerOptions = vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        output_face_blendshapes=False,
        running_mode=VisionRunningMode.VIDEO,
        num_faces=1
    )

    #カメラを起動
    cap = cv2.VideoCapture(0)
    #タクトスイッチ  pin40(GPIO21)を使用
    btn = gpiozero.DigitalInputDevice(pin=21,pull_up=False,)
    #圧電ブザー pin11(GPIO17)を使用
    buzzer = gpiozero.Buzzer(pin=17,initial_value=False)


    left_indices = [33, 160, 158, 133, 153, 144]
    right_indices = [362, 385, 387, 263, 373, 380]
    left_ear = 0.0
    right_ear = 0.0
    sleep_start_time=0

    #create_from_options 関数を使用してタスクを設定
    with FaceLandmarker.create_from_options(FaceLandmarkerOptions) as landmarker:
        while cap.isOpened():
            
            #タイマーが0になった時にボタンを押さずに終了させるための処理
            if is_finish:
                break
            
            #ボタンが押されたら終了
            if btn.value()==1:
                is_finish=True
                break
            
            #フレームを読み込む
            scucess,frame = cap.read()
            if not scucess:
                continue
            
            #フレームからランドマークを検出する処理
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            timestamp_ms = int((time.time()*1000))#秒単位からmsに変換
            #推論を実行(videoの場合はmsに変換したフレームのタイムスタンプも指定する)
            detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)

            #顔のランドマーク検出ができた時の処理
            if detection_result.face_landmarks:
                height, width = frame.shape[:2]
        
                for _, face_landmarks in enumerate(detection_result.face_landmarks):
                    #ピクセル座標系のランドマーク配列作成
                    landmarks_array = np.array([
                        (lm.x * width, lm.y * height)
                        for lm in face_landmarks
                    ])
                    
                    #目のランドマーク取得
                    left_eye_points = landmarks_array[left_indices]
                    right_eye_points = landmarks_array[right_indices]
                    
                    #両目のEARを計算
                    left_ear = calculate_eye_ratio(left_eye_points)
                    right_ear = calculate_eye_ratio(right_eye_points)
                    
                    #両目のEARの値が閾値(0.2)を下回った時の処理
                    if left_ear <0.2 and right_ear < 0.2:
                        if sleep_start_time == 0:
                            sleep_start_time = time.time()
                        elapsed_time = time.time()-sleep_start_time
                        #一定時間両目が閉じていたら is_sleeping をTrue(寝ていると判定)
                        if elapsed_time > 10:
                            #一定時間両目が閉じていたら寝ていると判定 & ブザーをオン
                            print("Sleeping")
                            is_sleeping=True
                            buzzer.on()
                    else:
                        #目が開いたらリセット & ブザーをオフ
                        sleep_start_time = 0  
                        is_sleeping = False
                        buzzer.off()
                        #この下に携帯電話の検出の処理を加える予定
                    
                    #検出結果を可視化するために imshowで描画する(本番ではコメントアウト)
                    cv2.putText(frame, f"EAR_L: {left_ear:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                        
                    cv2.putText(frame, f"EAR_R: {right_ear:.2f}", (250, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                    
                    cv2.imshow('FaceLandmerker', frame)
                    
            #顔のランドマーク検出ができなかった時の処理    
            else:
                sleep_start_time = 0 
                is_sleeping =True
            
            #ESCキーが押されると終了
            if cv2.waitKey(5) & 0xFF == 27:
                break

    #後処理                
    cap.release()            
    cv2.destroyAllWindows()        
    btn.close()
    buzzer.close()

    