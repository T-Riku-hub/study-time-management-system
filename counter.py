import LCD1602
import time

#グローバル変数を初期化
is_finish = False
is_detect_cell_phone=False
is_sleeping = False
total_time=0

#カウンターを制御する関数
def counter():
    global total_time 
    #LCDの表示を初期化
    LCD1602.init(0x27, 1)
    LCD1602.write(1, 0, 'Time:')
    LCD1602.write(15,0, "s") 
    LCD1602.write(1, 1, 'Studying...')
    
    #スレッド2でボタンが押されたら is_finish がTrueになり以下のループは終了
    while not is_finish:
        #寝ていないかつ携帯が検出されなければLCDの表示を更新 & 勉強時間+1秒
        if is_sleeping==False and is_detect_cell_phone==False: 
            LCD1602.write(11,0, f"{total_time}")
            total_time += 1
        time.sleep(1)
    LCD1602.clear()
    
    #勉強時間を 時間,分,秒の形に整形し、今回の勉強時間をLCDに表示
    hour = int(total_time/3600)
    minute = int((total_time%3600)/60)
    sec=   (total_time%3600)%60
    LCD1602.write(0, 0, 'Total Time')
    LCD1602.write(0, 1, f"{hour}h {minute}m {sec}s")

def counter_test():
    test_total_time=0
    LCD1602.init(0x27, 1)
    LCD1602.write(1, 0, 'Time:')
    LCD1602.write(15,0, "s") 
    LCD1602.write(1, 1, 'Studying...')
    while test_total_time<=60:
        LCD1602.write(11,0, f"{test_total_time}")
        test_total_time += 1
        time.sleep(1)
    LCD1602.clear()
    hour = int(test_total_time/3600)
    minute = int((test_total_time%3600)/60)
    sec=   (test_total_time%3600)%60
    LCD1602.write(0, 0, 'Total Time')
    LCD1602.write(0, 1, f"{hour}h {minute}m {sec}s")

if __name__=="__main__":
    counter_test()