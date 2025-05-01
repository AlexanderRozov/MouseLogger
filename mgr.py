from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Key, Listener as KeyboardListener
import threading
import time
import json

recording = False
replaying = False
events = []
mouse_controller = MouseController()

def record_mouse():
    def on_click(x, y, button, pressed):
        if recording and button == Button.left:
            events.append(["click", x, y, pressed, time.time()])
    def on_move(x, y):
        if recording:
            events.append(["move", x, y, time.time()])
    with mouse.Listener(on_click=on_click, on_move=on_move) as listener:
        listener.join()

def replay_events():
    global replaying
    while replaying:
        if not events:
            time.sleep(0.1)
            continue
        start_time = events[0][-1]
        for i, event in enumerate(events):
            if not replaying:
                break
            
            if event[0] == "move":
                if i % 3 != 0:  # пропускаем большинство движений
                    continue

            event_type = event[0]
            x = event[1]
            y = event[2]
            timestamp = event[-1]

            mouse_controller.position = (x, y)

            if event_type == "click":
                pressed = event[3]
                if pressed:
                    mouse_controller.press(Button.left)
                else:
                    mouse_controller.release(Button.left)

            # Задержка до следующего события
            if i < len(events) - 1:
                next_timestamp = events[i + 1][-1]
                delay = max(0.001, next_timestamp - timestamp)
                time.sleep(delay)

        time.sleep(0.2)  # Пауза между циклами

def on_press(key):
    global recording, replaying, events

    try:
        if key == Key.f2:
            if not recording:
                print("Запись началась...")
                events.clear()
                recording = True
            else:
                print("Запись остановлена.")
                recording = False

        elif key == Key.f3:
            if not replaying:
                print("Воспроизведение началось...")
                replaying = True
                threading.Thread(target=replay_events, daemon=True).start()
            else:
                print("Воспроизведение остановлено.")
                replaying = False

        elif key == Key.f5:
            with open("events.json", "w") as f:
                json.dump(events, f)
            print("Сценарий сохранён в events.json")

        elif key == Key.f9:
            with open("events.json", "r") as f:
                loaded = json.load(f)
                events.clear()
                for e in loaded:
                    events.append(e)
            print("Сценарий загружен из events.json")

    except Exception as e:
        print(f"Ошибка: {e}")

# Запуск
keyboard_listener = KeyboardListener(on_press=on_press)
keyboard_listener.start()
threading.Thread(target=record_mouse, daemon=True).start()

print("Скрипт запущен.")
print("F2 — запись, F3 — воспроизведение, F5 — сохранить, F9 — загрузить.")
keyboard_listener.join()
