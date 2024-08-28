import time
import json
import threading
import random
import tkinter as tk
from tkinter import messagebox
from pynput import keyboard
from pynput.keyboard import Controller, Key, Listener

# 전역 변수 설정
key_logs = []  # 키 로그를 저장할 리스트
collecting_logs = False  # 키 로그 수집 여부를 나타내는 플래그
macro_running = False  # 매크로 실행 여부를 나타내는 플래그
stop_event = threading.Event()  # 매크로 중지를 위한 이벤트
keyboard_controller = Controller()  # 키보드 조작을 위한 컨트롤러
key_logs_path = 'key_logs.json'  # 키 로그 파일 경로

def save_key_logs(logs):
    # 키 로그를 파일에 저장하는 함수
    with open(key_logs_path, 'w') as f:
        json.dump(logs, f, indent=4)

def load_key_logs():
    # 키 로그 파일을 로드하는 함수
    global key_logs
    with open(key_logs_path, 'r') as f:
        key_logs = json.load(f)

def info_message(title, message):
    # 정보 메시지를 표시하는 함수
    def close_messagebox():
        messagebox.destroy()
    
    messagebox = tk.Toplevel()
    messagebox.title(title)
    tk.Label(messagebox, text=message).pack(pady=10, padx=10)
    messagebox.after(2000, close_messagebox)  # 2초 후에 메시지 박스 닫기

def collect_keylogs():
    # 키 로그 수집을 시작하는 함수
    global collecting_logs, key_logs
    collecting_logs = True
    key_logs = []
    info_message("키 로그 수집", "키 로그 수집이 시작됩니다.")
    threading.Timer(2, start_collecting).start()  # 2초 대기 후 수집 시작

def start_collecting():
    # 키 로그 수집을 위한 리스너를 시작하는 함수
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def stop_collecting_keylogs():
    # 키 로그 수집을 중단하는 함수
    global collecting_logs
    collecting_logs = False
    save_key_logs(key_logs)
    info_message("키 로그 수집", "키 로그 수집이 중단되었습니다.")
    print("Key logs saved.")

def on_press(key):
    # 키가 눌렸을 때 호출되는 함수
    if collecting_logs:
        try:
            key_logs.append((time.time(), 'PRESS', key.char))
        except AttributeError:
            key_logs.append((time.time(), 'PRESS', str(key)))

def on_release(key):
    # 키가 놓였을 때 호출되는 함수
    if collecting_logs:
        try:
            key_logs.append((time.time(), 'RELEASE', key.char))
        except AttributeError:
            key_logs.append((time.time(), 'RELEASE', str(key)))

def run_macro():
    # 매크로를 실행하는 함수
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
    # 키 액션을 실행하는 함수
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
    # 매크로 실행을 시작하는 함수
    global macro_running, stop_event
    stop_event.clear()
    macro_running = True
    info_message("키 로그 반복", "키 로그 반복이 시작됩니다.")
    threading.Timer(2, lambda: threading.Thread(target=run_macro).start()).start()  # 2초 대기 후 매크로 시작

def stop_macro():
    # 매크로 실행을 중단하는 함수
    global macro_running
    macro_running = False
    stop_event.set()  # 이벤트를 설정하여 매크로 스레드를 중지
    info_message("키 로그 반복", "키 로그 반복이 중단되었습니다.")
    print("Macro stopped.")

def quit_program():
    # 프로그램을 종료하는 함수
    root.destroy()

# 단축키 핸들러 함수
def on_activate_collect():
    collect_keylogs()

def on_activate_stop_collect():
    stop_collecting_keylogs()

def on_activate_start_macro():
    start_macro()

def on_activate_stop_macro():
    stop_macro()

def on_activate_quit():
    quit_program()

# 단축키 리스너 설정
with Listener(
        on_press=None,
        on_release=None) as listener:

    # GUI 설정
    root = tk.Tk()  # 루트 윈도우 생성
    root.title("키 로그 매크로")  # 윈도우 타이틀 설정
    root.geometry("300x400")  # 창 크기 설정 (너비 x 높이)
    root.resizable(True, True)  # 창 크기 조정 가능

    frame = tk.Frame(root)  # 프레임 생성
    frame.pack(pady=20)  # 프레임 배치

    # 키 로그 수집 시작 버튼 (Ctrl + C)
    btn_collect = tk.Button(frame, text="키 로그 수집 시작 (Ctrl+C)", command=collect_keylogs)
    btn_collect.pack(pady=10)  # 버튼 배치

    # 키 로그 수집 중단 버튼 (Ctrl + S)
    btn_stop_collect = tk.Button(frame, text="키 로그 수집 중단 (Ctrl+S)", command=stop_collecting_keylogs)
    btn_stop_collect.pack(pady=10)  # 버튼 배치

    # 키 로그 반복 시작 버튼 (Ctrl + R)
    btn_repeat = tk.Button(frame, text="키 로그 반복 시작 (Ctrl+R)", command=start_macro)
    btn_repeat.pack(pady=10)  # 버튼 배치

    # 키 로그 반복 중단 버튼 (Ctrl + Q)
    btn_stop_repeat = tk.Button(frame, text="키 로그 반복 중단 (Ctrl+Q)", command=stop_macro)
    btn_stop_repeat.pack(pady=10)  # 버튼 배치

    # 프로그램 종료 버튼 (Ctrl + E)
    btn_quit = tk.Button(frame, text="프로그램 종료 (Ctrl+E)", command=quit_program)
    btn_quit.pack(pady=10)  # 버튼 배치

    # 단축키 조합과 해당 핸들러 연결
    with keyboard.GlobalHotKeys({
        '<ctrl>+c': on_activate_collect,
        '<ctrl>+s': on_activate_stop_collect,
        '<ctrl>+r': on_activate_start_macro,
        '<ctrl>+q': on_activate_stop_macro,
        '<ctrl>+e': on_activate_quit}) as h:
        root.mainloop()  # 이벤트 루프 시작
