import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np
import time
import threading
import gpiozero
import LCD1602
import write_DB
from counter_timer import counter_or_timer
from setup_timer import setup_time
from plot_png_file import plot_png_file
from send_mail import send_email
from datetime import datetime
from ultralytics import YOLO

#グローバル変数を初期化
is_finish = False
is_detect_cell_phone=False
is_sleeping = False
total_time=0

#カウンターを制御する関数
def counter():
    global total_time 
    LCD1602.init(0x27, 1)
    LCD1602.write(1, 0, 'Time:')
    LCD1602.write(15,0, "s") 
    LCD1602.write(1, 1, 'Studying...')
    while not is_finish:
        if is_sleeping==False and is_detect_cell_phone==False: 
            LCD1602.write(11,0, f"{total_time}")
            total_time += 1
        time.sleep(1)
    LCD1602.clear()
    hour = int(total_time/3600)
    minute = int((total_time%3600)/60)
    sec=   (total_time%3600)%60
    LCD1602.write(0, 0, 'Total Time')
    LCD1602.write(0, 1, f"{hour}h {minute}m {sec}s")

#タイマーを制御する関数
def timer(current_time):
    global is_finish
    global total_time
    LCD1602.init(0x27, 1)
    while not is_finish:
        if current_time<=0:
            is_finish=True
            break
        if is_sleeping==False and is_detect_cell_phone==False: 
            LCD1602.clear() 
            LCD1602.write(0, 0, 'Time:')
            LCD1602.write(11,0, f"{current_time}")
            LCD1602.write(15,0, "s") 
            LCD1602.write(1, 1, 'Studying...')
            current_time -= 1
            total_time+=1
        time.sleep(1)
    LCD1602.clear()
    hour = int(total_time/3600)
    minute = int((total_time%3600)/60)
    sec=   (total_time%3600)%60
    LCD1602.write(0, 0, 'Total Time')
    LCD1602.write(0, 1, f"{hour}h {minute}m {sec}s")

def calculate_eye_ratio(eye_landmarks):
    v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
    h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
    ear = (v1 + v2) / (2.0 * h) if h > 0 else 0
    return ear

def detect_sleep_and_cell_phone():
    #モデルのパスを指定
    model_path_landmarker = "./models/face_landmarker.task"

    BaseOptions = python.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    #ランドマーク検出器のオプションを指定
    FaceLandmarkerOptions = vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path_landmarker),
        output_face_blendshapes=False,
        running_mode=VisionRunningMode.VIDEO,
        num_faces=1
    )
    
    #ランドマーク検出を行うモデルと物体検出を行うモデルを作成
    landmarker = FaceLandmarker.create_from_options(FaceLandmarkerOptions) 
    model = YOLO("./models/best_int8.tflite")
    
    global is_sleeping
    global is_detect_cell_phone
    global is_finish
    
    left_indices = [33, 160, 158, 133, 153, 144]
    right_indices = [362, 385, 387, 263, 373, 380]
    left_ear = 0.0
    right_ear = 0.0
    sleep_start_time=0

    #カメラ起動
    cap = cv2.VideoCapture(0)
    #タクトスイッチ  pin40を使用
    btn = gpiozero.DigitalInputDevice(pin=21,pull_up=False,)
    buzzer = gpiozero.Buzzer(pin=19,initial_value=False)
    try:
        while cap.isOpened():
            #タイマーが0になった時に、ボタンを押さずに終了させるための処理
            if is_finish:
                break
            
            #ボタンが押されたら終了
            if btn.value == 1:
                is_finish = True
                break
            
            scucess,frame = cap.read()
            if not scucess:
                continue
            
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            timestamp_ms = int(time.time() * 1000)
            #ランドマーク検出
            #videoの場合はmsに変換したフレームのタイムスタンプも指定する。
            detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)

            if detection_result.face_landmarks:
                height, width = frame.shape[:2]
                
                #１人分のランドマーク座標を処理
                for _, face_landmarks in enumerate(detection_result.face_landmarks):
                    
                    #ピクセル座標系のランドマーク配列作成
                    landmarks_array = np.array([
                        (lm.x * width, lm.y * height)
                        for lm in face_landmarks
                    ])
                    
                    #特定のランドマークのみを取得
                    left_eye_points = landmarks_array[left_indices]
                    right_eye_points = landmarks_array[right_indices]
                    
                    #両目のEAR算出
                    left_ear = calculate_eye_ratio(left_eye_points)
                    right_ear = calculate_eye_ratio(right_eye_points)
                    
                    #両目のEARの値が閾値を下回った時の処理
                    if left_ear <0.17 and right_ear < 0.17:
                        if sleep_start_time == 0:
                            sleep_start_time = time.time()
                        elapsed_time = time.time()-sleep_start_time
                        if elapsed_time > 5:
                            #約5秒間両目が閉じていたら寝ていると判定 & ブザーをオン
                            print("Sleeping")
                            is_sleeping=True
                            buzzer.on()
                        cv2.putText(frame, f"EAR_L: {left_ear:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                            
                        cv2.putText(frame, f"EAR_R: {right_ear:.2f}", (190, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                        
                        cv2.imshow('frame', frame)
                    else:
                        # 目が開いたらリセット & ブザーをオフ
                        is_sleeping = False
                        buzzer.off()
                        #物体検出を実行
                        results = model(frame,verbose=False,save=False,conf=0.5)
                        for result in results:
                            boxes = result.boxes
                            #スマートフォンを検出
                            if len(boxes)>=1:
                                is_detect_cell_phone=True
                                break
                            #スマートフォンが検出されなかった
                            else:
                                is_detect_cell_phone=False
                                
                        annotated = results[0].plot()
                        
                        cv2.putText(annotated, f"EAR_L: {left_ear:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2) 
                        cv2.putText(annotated, f"EAR_R: {right_ear:.2f}", (250, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2)
                        cv2.imshow('frame', annotated)
            #顔のランドマークが検出できなかった時
            else:
                is_sleeping=True #寝ていない場合もあるがこのフラグをTrueにする
                sleep_start_time = 0 
                    
            if cv2.waitKey(5) & 0xFF == 27:
                is_finish=True
                break
            #処理の負荷を抑えるため0.075秒間隔でループを回す
            time.sleep(0.075)
        
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        landmarker.close()
        btn.close()
        buzzer.close()


#最初の入力でカウンターかタイマーを選択
Counter_OR_Timer = counter_or_timer()

if Counter_OR_Timer==1:
    #カウンターの時の処理
    thread_1 = threading.Thread(target=counter)
else:
    #タイマーの時の処理
    current_time = setup_time()
    thread_1 = threading.Thread(target=timer,args=(current_time,))

#タイマーをスレッド1で実行開始
thread_1.start()
#睡眠検知とスマートフォンの検知をメインで実行
detect_sleep_and_cell_phone()
#メインの処理が終了したら、スレッドを終了
thread_1.join()

#現在の日時を取得
now = datetime.now()

write_DB.write_SQL(now,total_time)
write_DB.write_notion_db(now,total_time)
today_study_time_str, csv_data, sum_study_time = plot_png_file()
print("グラフの保存が完了しました")
send_email(
    total_time=total_time,
    date_str=f"{now.year}/{now.month}/{now.day}",
    today_study_time_str=today_study_time_str,
    csv_data=csv_data, 
    sum_study_time=sum_study_time,
    send_file="result.png")
print('メールを送信しました')
