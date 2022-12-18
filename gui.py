import tkinter as tk
import tkinter.font
import tkinter.ttk as ttk
from tkinter import messagebox
import cv2
import numpy as np
from time import sleep
from subprocess import run, PIPE

_DIR_ANDROID_CAPTURE = "/sdcard/_capture.png"                               #Emu側のスクショ保存場所
_DIR_INTERNAL_CAPTURE_FOLDER = "C:/Arknights_capture_img"                   #PC側のスクショ保存フォルダの場所
_DIR_INTERNAL_CAPTURE = "C:/Arknights_capture_img/_capture.png"                                  #PC側のスクショ保存場所

_DIR_TEMP1 = "img/temp1.png"  #それぞれ判定用の画像
_DIR_TEMP2 = "img/temp2.png"
_DIR_TEMP3 = "img/temp3.png"
_DIR_TEMP4 = "img/temp4.png"

_THRESHOLD = 0.9 #どのくらいの精度で判定するか
_DIR_TEMP = [_DIR_TEMP4, _DIR_TEMP1, _DIR_TEMP2, _DIR_TEMP3] #判定のリスト化＆判定の順番


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# GUI ボタン関数

def start_func():
    global root
    global start
    global loop_label
    loop_label["text"] = "状態：周回中"
    if connect_label["text"] == "接続状況：接続成功":
        start = root.after(
            2000,
            start_func
        )
        # ここに周回の関数を挿入 ※while文は外して
        capture_screen(_DIR_ANDROID_CAPTURE, _DIR_INTERNAL_CAPTURE_FOLDER)
        for i in _DIR_TEMP:
            x, y = get_center_position_from_tmp(_DIR_INTERNAL_CAPTURE , i)
            if x >= 0 and y >= 0:
                tap(x, y)
                sleep(1)
                break   
        
    else:
        loop_label["text"] = "状態：エラー"

def loop_stop():
    root.after_cancel(start)
    loop_label["text"] = "状態：待機中"

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Android 接続関数

def doscmd(directory, command):
    global connect_label
    completed_process = run(command, stdout=PIPE, shell=True, cwd=directory, universal_newlines=True, timeout=10)
    if "bad" in completed_process.stdout or completed_process.stdout == None:
        connect_label["text"] = "接続状況：接続失敗"
        port_entry.delete(0,tk.END)
    else:
        connect_label["text"] = "接続状況：接続成功"

def send_cmd_to_adb(cmd):
    _dir = "C:/Program Files/BlueStacks_nxt"
    return doscmd(_dir, cmd)

def connect_adb():
    _cmd = "HD-Adb connect 127.0.0.1:" + str(port_entry.get())
    send_cmd_to_adb(_cmd)

def capture_screen(dir_android, folder_name):
    _cmd = "HD-Adb shell screencap -p" + " " + dir_android
    _pipe = send_cmd_to_adb(_cmd)

    _cmd = "HD-Adb pull" + " " + dir_android + " " + folder_name
    send_cmd_to_adb(_cmd)

def get_center_position_from_tmp(dir_input, dir_tmp):
    _input = cv2.imread(dir_input)
    _temp = cv2.imread(dir_tmp)

    cv2.cvtColor(_input, cv2.COLOR_RGB2GRAY)
    cv2.cvtColor(_temp, cv2.COLOR_RGB2GRAY)

    _h, _w, _none  = _temp.shape

    _match = cv2.matchTemplate(_input, _temp, cv2.TM_CCOEFF_NORMED)
    _loc = np.where(_match >= _THRESHOLD)
    try:
        _x = _loc[1][0]
        _y = _loc[0][0]
        return _x + _w / 2, _y + _h / 2
    except IndexError as e:
        return -1, -1

def tap(x, y):
    _cmd = "HD-Adb shell input touchscreen tap"+ " " + str(x) + " " + str(y)
    send_cmd_to_adb(_cmd)

# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

root = tk.Tk()
root.geometry("350x100")
font = tkinter.font.Font(
    root,
    family = "Times",
    size = 15
)

connect_label = tk.Label(
    root,
    text= "接続状況：未接続",
    relief=tk.RIDGE, bd=2,
)

connect_label.place(
    x = 0,
    y = 2,
)

loop_label = tk.Label(
    root,
    text="状態：待機中",
    relief=tk.RIDGE, bd=2,
)

loop_label.place(
    x= 220,
    y= 2,
)

run_button =ttk.Button(
    root,
    text= "Run",
    command = start_func,
)

run_button.place(
    x=220,
    y=35,
)

stop_button =ttk.Button(
    root,
    text= "Stop",
    command= loop_stop,
)

stop_button.place(
    x=220,
    y=70,
)

connect_button =ttk.Button(
    root,
    text= "Connect",
    command= connect_adb,
)

connect_button.place(
    x=0,
    y=70
    )

port_entry = ttk.Entry(
    root,
)

port_entry.place(
    x= 0,
    y= 36,
)

root.mainloop()