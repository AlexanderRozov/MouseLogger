from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Key, Listener as KeyboardListener
import threading
import time
import json

# Состояния
recording = False
replaying = False
events = []
mouse_controller = MouseController()

def record_mouse():
    def on_click(x, y, button, pressed):
        if recording and button == Button.left:
            events.append(('click', x, y, pressed, time.time()))
    def on_move(x, y):
        if recording:
            events.append(('move', x, y, time.time()))
    with mouse.Listener(on_click=on_click, on_move=on_move) as listener:
        listener.join()
        

def replay_events():
    global replaying
    while replaying:
        if not events:
            time.sleep(0.1)
            continue
        start_time = events[0][-1]
        for event in events:
            if not replaying:
                break
            if event[0] == 'move':
                _, x, y, timestamp = event
                mouse_controller.position = (x, y)
            elif event[0] == 'click':
                _, x, y, pressed, timestamp = event
                mouse_controller.position = (x, y)
                if pressed:
                    mouse_controller.press(Button.left)
                else:
                    mouse_controller.release(Button.left)
            # Подождать до следующего события
            time.sleep(0.01)
        time.sleep(0.2)  # Пауза между циклами

def on_press(key):
    global recording, replaying, events

    try:
        if key == keyboard.Key.f2:
            if not recording:
                print("Запись началась...")
                events = []
                recording = True
            else:
                print("Запись остановлена.")
                recording = False
        elif key == keyboard.Key.f3:
            if not replaying:
                print("Воспроизведение началось...")
                replaying = True
                threading.Thread(target=replay_events, daemon=True).start()
            else:
                print("Воспроизведение остановлено.")
                replaying = False
        if key == keyboard.Key.f5:
            with open("events.json", "w") as f:
                json.dump(events, f)
        if key == keyboard.Key.f9:
            with open("events.json", "r") as f:
                events = json.load(f)
            
                    
    except AttributeError:
        pass

# Запуск слушателя клавиатуры
keyboard_listener = KeyboardListener(on_press=on_press)
keyboard_listener.start()

# Запуск записи мыши в отдельном потоке
threading.Thread(target=record_mouse, daemon=True).start()

print("Скрипт запущен. Нажмите F2 для записи, F3 для воспроизведени, F5 сохранить скрипть в файле, F9 загрузить скрипт из файла")
keyboard_listener.join()
