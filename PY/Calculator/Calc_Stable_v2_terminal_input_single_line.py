
import keyboard
start=True

while start == True:
    calculate = (input("Calculator active: "))
    try:
        print(calculate," = ",eval(calculate))
    except:
        print("error")
        print("input not a number or an operator")
