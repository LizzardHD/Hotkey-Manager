import keyboard
import mouse
import time
import threading
from typing import Callable

stop_command = False
# Function to add a hotkey with a loop
def Hotkey(actionlist:type[list],printer: Callable):
    running = False
    falling_trigger = False
    for action in actionlist:
        if action[0] == "Hotkey":
            myhotkey = action[1]
            break

    def loop_function():
        global stop_command
        while not stop_command:
            if running:
                for key, value in actionlist:
                    if key == "Sleep":
                        try:
                            value = float(value)
                            time.sleep(value)
                        except Exception as e:
                            print(f"{e} Fault at key {key} with value: {value}")
                            continue
                    elif key == "Mouse Click":
                        mouse.click(value)  # 'value' should be 'left', 'right', or 'middle'
                    elif key == "Mouse Double Click":
                        mouse.double_click(value)  # 'value' should be 'left', 'right', or 'middle'
                    elif key == "Mouse Press":
                        mouse.press(value)  # 'value' should be 'left', 'right', or 'middle'
                    elif key == "Mouse Release":
                        mouse.release(value)  # 'value' should be 'left', 'right', or 'middle'
                    elif key == "Mouse Move":
                        x, y = map(int, value.split(','))
                        mouse.move(x, y,False)
                    elif key == "Absolute Mouse Move":
                        x, y = map(int, value.split(','))
                        mouse.move(x, y,True)
                    elif key == "Mouse Wheel":
                        delta = int(value)
                        mouse.wheel(delta)
                    elif key == "Keyboard Send":
                        keyboard.send(value)
                    elif key == "Keyboard Write":
                        keyboard.write(value)
                    elif key == "Keyboard Press":
                        keyboard.press(value)
                    elif key == "Keyboard Release":
                        keyboard.release(value)

    def on_hotkey_event(e):
        nonlocal running, falling_trigger

        if e.event_type == keyboard.KEY_DOWN:
            if not falling_trigger:
                running = not running
                falling_trigger = True
                if running:
                    printer("Loop started")
                else:
                    printer("Loop stopped")

        elif e.event_type == keyboard.KEY_UP:
            falling_trigger = False

    printer("Press %s to start/stop the loop." % myhotkey)
    keyboard.on_press_key(myhotkey, on_hotkey_event)
    keyboard.on_release_key(myhotkey, on_hotkey_event)
    threading.Thread(target=loop_function).daemon = True  # Daemonize the thread to allow for clean exit
    threading.Thread(target=loop_function).start()


