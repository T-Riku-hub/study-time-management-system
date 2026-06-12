import time
import setup_timer

def counter_or_timer():
    print("Counter --> 1")
    print("Timer --> 2")
    
    while True:
        Counter_OR_Timer = input("Timer or Counter ? : ")
        #Counter : 1
        if int(Counter_OR_Timer) == 1:
            return 1
        #Timer : 2
        elif int(Counter_OR_Timer) ==2:
            return 2
        else:
            continue

def counting():
    #テスト用の擬似的なカウンター
    total_time=0
    while total_time<=30:
        print(f"Now Time : {total_time}s")
        total_time+=1
        time.sleep(1)

def timer(total_time):
    #テスト用の擬似的なタイマー
    while total_time>=0:
        print(f"Now Time : {total_time}s")
        total_time-=1
        time.sleep(1)

if __name__ == "__main__":
    Counter_OR_Timer = counter_or_timer()
    if Counter_OR_Timer == 1:
        counting()
    else:
        total = setup_timer.setup_time()
        timer(total)