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
            try:
                line = ser.readline().decode('utf-8').rstrip()
                items = line.split()
                dist = int(items[0])
                angl_read = float(items[4])  # 角度資訊

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
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(12, 8))  # 設定圖形大小
#fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(12, 12),facecolor='black')  # 設定圖形大小


dist_read = 0
angl_read = 0

# 設定半徑範圍（最大100公分）
rmax=110
ax.set_rmax(rmax)  # 設定最大半徑，根據您的需求進行調整

# 設定方位角範圍（僅顯示0-90度）
#ax.set_theta_offset(np.pi / 2)  # 設定方位偏移，使0度在圓心上方
#ax.set_theta_direction(-1)  # 逆時針方向繪製圖形
#ax.set_thetamin(90)  # 設定最小方位角
#ax.set_thetamax(270)  # 設定最大方位角
# 設定方位角範圍（僅顯示0-90度）
ax.set_theta_offset(np.pi / 2)  # 設定方位偏移，使0度在圓心上方
#ax.set_theta_direction(-1)  # 逆時針方向繪製圖形
ax.set_thetamin(-45)  # 設定最小方位角
ax.set_thetamax(45)  # 設定最大方位角
angle_shift = -45

# 移除坐標軸標籤
ax.set_xticks([])

# 設定半徑標籤，包括單位 "CM"，以及字體大小
ax.set_yticks(range(0, 101, 20))
ax.set_yticklabels([str(i)+"cm" for i in range(0, 101, 20)], color='green', fontsize=20)  # 調整字體大小和顏色

# 設定坐標軸線條寬度
ax.spines['polar'].set_linewidth(2)

# 初始化紅點和綠光柱
red_point = None
green_bars = []  # 用於存儲多層綠色光柱
green_bar = None
green_bar2 = None
red_points_ang = []
red_points_dis = []
red_points_alp = []


# 設定綠色光柱的殘影效果
max_green_layers = 10  # 最大保留的綠色光柱層數
fade_alpha = 0.2  # 殘影的透明度衰減率

# 旋轉整個雷達圖，包括底圖和標示，使45度位置朝向畫面正上方
ax.set_theta_zero_location('N')  # 改為 'S'

ax.set_facecolor('white')
#ax.xaxis.grid(color='blue', linestyle='-', linewidth=1)
#ax.yaxis.grid(color='white', linestyle='-', linewidth=1)

# 在雷達圖上畫出扇形區域的白色線
#theta_values = np.deg2rad(np.arange(90, 271, 1))  # 角度值，這裡假設從90度到270度，可以根據需要調整
#r_values = np.full_like(theta_values, rmax)  # 半徑值，全部設為最大半徑

#####################################################################################################
##### 平行執行，並不停刷新distance與velocity的數值
#####################################################################################################
thread = threading.Thread(target=read_serial)
thread.daemon = True  # 设置线程为守护线程，以便在主线程结束时自动退出
thread.start()

# 開始讀取和繪製雷達圖
try:
    while True:
        # 將距離限制在100公分以內
        dist = min(dist_read, rmax)
        distance = float(dist)

        # 設定角度（弧度）
        angle_rad = np.deg2rad(angl_read+ + angle_shift)  # 使用角度資訊設定方位角


        # 繪製多層漸層綠色光柱
        for i in range(max_green_layers):
            alpha = max(0.,1.0 - (i * fade_alpha))  # 計算透明度
            green_bar = ax.bar(angle_rad, dist, width=np.deg2rad(i), color='green', alpha=alpha)
            green_bars.append(green_bar)

            # 如果光柱層數超過最大值，刪除最舊的光柱
            if len(green_bars) > max_green_layers:
                old_bar = green_bars.pop(0)
                old_bar.remove()



        # 繪製雷達圖上的紅點
        if red_point is not None:
            red_point.remove()
            red_point = None
        if dist < rmax:
            red_points_ang.append(angle_rad)
            red_points_dis.append(dist)
            red_points_alp.append(1.)
        #red_point = ax.scatter(red_points_ang, red_points_dis, c='red', s=150, alpha=red_points_alp)
        red_point = ax.scatter(red_points_ang, red_points_dis, c='red', s=150, alpha=red_points_alp)  # 紅點


        #print(len(red_points_alp),dist_read,angl_read)
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
