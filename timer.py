import LCD1602
import time

#グローバル変数を初期化
is_finish = False
is_detect_cell_phone=False
is_sleeping = False
total_time=0

#タイマーを制御する関数
def timer(current_time):
    global is_finish
    global total_time
    LCD1602.init(0x27, 1)
    
    #スレッド2でボタンが押されら is_finish がTrueになり以下のループは終了
    while not is_finish:
        #タイマーが０になると計測終了
        if current_time<=0:
            is_finish=True
            break
        #寝ていないかつ携帯が検出されなければLCDの表示を更新 & 勉強時間+1秒
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
    
    #勉強時間を 時間,分,秒の形に整形し、今回の勉強時間をLCDに表示
    hour = int(total_time/3600)
    minute = int((total_time%3600)/60)
    sec=   (total_time%3600)%60
    LCD1602.write(0, 0, 'Total Time')
    LCD1602.write(0, 1, f"{hour}h {minute}m {sec}s")