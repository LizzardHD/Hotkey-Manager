import keyboard
import time
import threading

i = 0
counter = 0  
running = threading.Event()

myHotkey = "space"

def do_thing():
    global running
    while running:
        print("doing thing")
        time.sleep(0.5)
    return

def thread_function():
    global running    
    while running.is_set():
        time.sleep(0.4)
        print("statement")



#keyboard.press_and_release(myHotkey, OnOff)




while True:
    keyboard.wait(myHotkey, trigger_on_release=True)
    if running.is_set():
        running.clear()     
    else:
        running.set()
        
    if running.is_set():
        executingThread = threading.Thread(target= thread_function)
        executingThread.start() 
    print(threading.active_count())