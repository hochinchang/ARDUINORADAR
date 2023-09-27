import serial
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import statistics
import threading


#####################################################################################################
##### 從USB端口讀取Arduino的數值資訊
#####################################################################################################
def read_serial():
    global dist_read
    global angl_read
    distance_list = []
    outlier_threshold_d = 2
    num_distance = 1
    while True:

        if ser.in_waiting > 0:
            print('aaa', ser.in_waiting)
            try:
                line = ser.readline().decode('utf-8').rstrip()
                items = line.split()
                dist = int(items[0])
                angl_read = float(items[4])  # 角度資訊
                print(line)

            except:
                pass
            else:
                # 距離計算
                distance_list.append(dist)
                if len(distance_list) < 3:
                    dist_read = sum(distance_list) / len(distance_list)
                else:
                    std_dev = statistics.stdev(distance_list)
                    mean = statistics.mean(distance_list)
                    filtered_distance_list = [num for num in distance_list if
                                              abs(num - mean) <= outlier_threshold_d * std_dev]
                    dist_read = sum(filtered_distance_list) / len(filtered_distance_list)
                    if len(distance_list) > num_distance:
                        del distance_list[0]

# 設定串口，根據您的 Arduino 端口進行調整
ser = serial.Serial('COM5', 9600)

# 設定全局字體大小
mpl.rcParams['font.size'] = 25  # 調整字體大小

# 初始化雷達圖，設定圖形大小為800x800
plt.ion()  # 啟用互動模式
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(12, 12))  # 設定圖形大小


dist_read = 0
angl_read = 0

# 設定半徑範圍（最大100公分）
rmax=120
ax.set_rmax(rmax)  # 設定最大半徑，根據您的需求進行調整

# 設定方位角範圍（僅顯示0-90度）
ax.set_theta_offset(np.pi / 2)  # 設定方位偏移，使0度在圓心上方
ax.set_theta_direction(-1)  # 逆時針方向繪製圖形
ax.set_thetamin(90)  # 設定最小方位角
ax.set_thetamax(270)  # 設定最大方位角

# 移除坐標軸標籤
ax.set_xticks([])

# 設定半徑標籤，包括單位 "CM"，以及字體大小
ax.set_yticks(range(0, 101, 20))
ax.set_yticklabels([str(i) for i in range(0, 101, 20)])  # 調整字體大小

# 設定坐標軸線條寬度
ax.spines['polar'].set_linewidth(2)

# 初始化紅點和綠光柱
red_point = None
green_bar = None
red_points_ang = []
red_points_dis = []
red_points_alp = []

# 旋轉整個雷達圖，包括底圖和標示，使45度位置朝向畫面正上方
ax.set_theta_zero_location('S')  # 改為 'S'


#####################################################################################################
##### 平行執行，並不停刷新distance與velocity的數值
#####################################################################################################
thread = threading.Thread(target=read_serial)
thread.daemon = True  # 设置线程为守护线程，以便在主线程结束时自动退出
thread.start()

# 開始讀取和繪製雷達圖
try:
    while True:
        #try:
        #    line = ser.readline().decode('utf-8').rstrip()
        #    items = line.split()
        #    dist = int(items[0])  # 距離資訊
        #    angl = float(items[4])  # 角度資訊
        #except:
        #    continue

        # 將距離限制在100公分以內
        dist = min(dist_read, rmax)
        distance = float(dist)

        # 設定角度（弧度）
        angle_rad = np.deg2rad(135+angl_read)  # 使用角度資訊設定方位角

        # 繪製雷達圖上的綠光柱
        if green_bar is not None:
            green_bar.remove()
        green_bar = ax.bar(angle_rad, dist, width=np.deg2rad(5), color='green', alpha=0.5)

        # 繪製雷達圖上的紅點
        if red_point is not None:
            red_point.remove()
            red_point = None
        if dist < rmax:
            red_points_ang.append(angle_rad)
            red_points_dis.append(dist)
            red_points_alp.append(1.)

        red_point = ax.scatter(red_points_ang, red_points_dis, c='red', s=150, alpha=red_points_alp)

        print(len(red_points_alp),dist_read,angl_read)
        for i in range(len(red_points_alp)):
            red_points_alp[i] = max(0, red_points_alp[i] - 0.05)
        for i in range(len(red_points_alp) - 1, 0, -1):
            if red_points_alp[i] <= 0.:
                del red_points_ang[i]
                del red_points_dis[i]
                del red_points_alp[i]

        plt.pause(0.01)  # 暫停一小段時間以更新圖形

except KeyboardInterrupt:
    ser.close()  # 在結束時關閉串口
    print("程式已結束")
