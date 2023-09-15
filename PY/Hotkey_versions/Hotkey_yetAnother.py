import keyboard
import time
import threading

def add_Hotkey(myhotkey, actionlist, timelist):
    running = False
    falling_trigger = False

    def loop_function():
        while True:
            if running:
                for action, sleep in zip(actionlist, timelist):
                    print(action)
                    time.sleep(sleep)

    def on_hotkey_event(e):
        nonlocal running, falling_trigger

        if e.event_type == keyboard.KEY_DOWN:
            if not falling_trigger:
                running = not running
                falling_trigger = True
                print("Loop", "started" if running else "stopped")
                time.sleep(0.1)
        elif e.event_type == keyboard.KEY_UP:
            falling_trigger = False

    print("Press %s to start/stop the loop." % myhotkey)
    keyboard.on_press_key(myhotkey, on_hotkey_event)
    keyboard.on_release_key(myhotkey, on_hotkey_event)

    thread = threading.Thread(target=loop_function)
    thread.daemon = True  # Daemonize the thread to allow for clean exit
    thread.start()

    try:
        while True:
            time.sleep(0.1)  # Main thread can sleep without blocking the hotkey events
    except KeyboardInterrupt:
        pass

add_Hotkey("space", ["one", "two", "three"], [1, 2, 3])