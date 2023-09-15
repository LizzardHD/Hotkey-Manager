
import keyboard
start=True

while start == True:
    keyboard.write("Calculator active: ",delay=0.02)
    keyboard.send("enter")
    calculate = list(keyboard.get_typed_strings(keyboard.record('enter')))[0]
    try:
        keyboard.write(str(calculate)+" = "+str(eval(calculate)),delay=0.02) 
        keyboard.send("enter")
    except:
        keyboard.write("error",delay=0.02)
        keyboard.send("enter")
        keyboard.write("input not an operator or a number!",delay=0.02)
        keyboard.send("enter")
        keyboard.write(calculate)
        keyboard.send("enter")
"""


Calculator active: 
2**2+6*6
2**2+6*6 = 40
Calculator active: 
(2**2+6)*6
error
input not an operator or a number!
(2**2+6
Calculator active: 
(2**2+6)*6
(2**2+6)*6 = 60
Calculator active: 




"""