import time
import json
import threading
import tkinter as tk
from tkinter import messagebox
from pynput import keyboard
from pynput.keyboard import Controller, Key

# 전역 변수 설정
key_logs = []
collecting_logs = False
macro_running = False
stop_event = threading.Event()
keyboard_controller = Controller()
key_logs_path = 'key_logs.json'  # 키 로그 파일 경로

def save_key_logs(logs):
    with open(key_logs_path, 'w') as f:
        json.dump(logs, f, indent=4)

def load_key_logs():
    global key_logs
    with open(key_logs_path, 'r') as f:
        key_logs = json.load(f)

def info_message(title, message):
    def close_messagebox():
        messagebox.destroy()
    
    messagebox = tk.Toplevel()
    messagebox.title(title)
    tk.Label(messagebox, text=message).pack(pady=10, padx=10)
    messagebox.after(2000, close_messagebox)  # 2초 후에 메시지 박스 닫기

def collect_keylogs():
    global collecting_logs, key_logs
    collecting_logs = True
    key_logs = []
    info_message("키 로그 수집", "키 로그 수집이 시작됩니다.")
    threading.Timer(2, start_collecting).start()  # 2초 대기 후 수집 시작

def start_collecting():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def stop_collecting_keylogs():
    global collecting_logs
    collecting_logs = False
    save_key_logs(key_logs)
    info_message("키 로그 수집", "키 로그 수집이 중단되었습니다.")
    print("Key logs saved.")

def on_press(key):
    if collecting_logs:
        try:
            key_logs.append((time.time(), 'PRESS', key.char))
        except AttributeError:
            key_logs.append((time.time(), 'PRESS', str(key)))

def on_release(key):
    if collecting_logs:
        try:
            key_logs.append((time.time(), 'RELEASE', key.char))
        except AttributeError:
            key_logs.append((time.time(), 'RELEASE', str(key)))

def run_macro():
    global macro_running, key_logs
    load_key_logs()
    repeat_count = 0
    start_time = time.time()
    while macro_running and repeat_count < 19:
        for log in key_logs:
            if not macro_running:
                break
            timestamp, action, key = log
            current_time = time.time()
            elapsed_time = current_time - start_time
            delay = timestamp - key_logs[0][0] - elapsed_time  # Adjust delay
            if delay > 0:
                time.sleep(delay)
            print(f"Executing {action} on key {key} after {elapsed_time:.4f} seconds")
            execute_key_action(action, key)
        repeat_count += 1
        start_time = time.time()
        print(f"Completed iteration {repeat_count}")

def execute_key_action(action, key):
    try:
        if action == 'PRESS':
            if key.startswith('Key.'):
                special_key = getattr(Key, key.split('.')[1])
                keyboard_controller.press(special_key)
            else:
                keyboard_controller.press(key)
        elif action == 'RELEASE':
            if key.startswith('Key.'):
                special_key = getattr(Key, key.split('.')[1])
                keyboard_controller.release(special_key)
            else:
                keyboard_controller.release(key)
    except AttributeError:
        pass

def start_macro():
    global macro_running, stop_event
    stop_event.clear()
    macro_running = True
    info_message("키 로그 반복", "키 로그 반복이 시작됩니다.")
    threading.Timer(2, lambda: threading.Thread(target=run_macro).start()).start()  # 2초 대기 후 매크로 시작

def stop_macro():
    global macro_running
    macro_running = False
    stop_event.set()  # 이벤트를 설정하여 매크로 스레드를 중지
    info_message("키 로그 반복", "키 로그 반복이 중단되었습니다.")
    print("Macro stopped.")

def quit_program():
    save_key_logs(key_logs)
    root.destroy()

# GUI 설정
root = tk.Tk()
root.title("키 로그 매크로")
root.geometry("400x300")  # 초기 창 크기 설정 (너비 x 높이)

frame = tk.Frame(root)
frame.pack(pady=20)

btn_collect = tk.Button(frame, text="키 로그 수집 시작", command=collect_keylogs)
btn_collect.pack(pady=10)

btn_stop_collect = tk.Button(frame, text="키 로그 수집 중단", command=stop_collecting_keylogs)
btn_stop_collect.pack(pady=10)

btn_repeat = tk.Button(frame, text="키 로그 반복 시작", command=start_macro)
btn_repeat.pack(pady=10)

btn_stop_repeat = tk.Button(frame, text="키 로그 반복 중단", command=stop_macro)
btn_stop_repeat.pack(pady=10)

btn_quit = tk.Button(frame, text="프로그램 종료", command=quit_program)
btn_quit.pack(pady=10)

root.mainloop()
