#タイマーの時間を設定するための関数
def setup_time():
    while True:
        hour = input("input hour (0~12): ")
        hour = int(hour)
        if 0<=hour<=12:
            break

    while True:
        minute = input("input minute (1~59): ")
        minute = int(minute)
        if 1<=minute<=59:
            break

    hour = hour*60*60
    minute = minute*60

    total_time = hour+minute
    return total_time