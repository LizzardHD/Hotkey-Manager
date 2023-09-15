import keyboard
import time
running = False
i = 0
counter = 0  

myHotkey = "space"

def do_iterative(): #custom code
    global i 
    print(i)
    time.sleep(0.4)
    i = i+1


"""
def Turn_on_off(): #Hotkey Callback Function
    global running
    if running == False:
        running = True
        print("starting...")
    elif running == True:
        running = False
        print("ending...")        
    return running
"""
    
def Turn_on_off(): #Hotkey Callback Function
    global running
    if running == False:
        running = True
        print("starting...")
    elif running == True:
        running = False
        print("ending...")        
    return running

keyboard.register_hotkey(myHotkey,Turn_on_off, trigger_on_release=True)
    
while True:
    while not running:
        print("Programm stopped, press space to start")
        keyboard.wait(myHotkey)
                         
    while running:
        if counter == 0:
            print("Program started, press space to stop")
        counter = counter+1 
        do_iterative()  
             


    