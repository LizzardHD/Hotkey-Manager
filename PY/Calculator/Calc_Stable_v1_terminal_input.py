

def multiply(args):
    start = args[0]
    for each in args[1:]:
        result = start * each
        print(start," times ",each," = ",result)
        start = result
    return
    
def divide(args):
    start = args[0]
    for each in args[1:]:
        result = start / each
        print(start," divided by ",each," = ",result)
        start = result
    return

    
def subtract(args):
    start = args[0]
    for each in args[1:]:
        result = start - each
        print(start," minus ",each," = ",result)
        start = result
    return

def add(args):
    start = args[0]
    for each in args[1:]:
        result = start + each
        print(start," plus ",each," = ",result)
        start = result
    return

def power(args):
    start = args[0]
    for each in args[1:]:
        result = start ** each
        print(start," by the power of ",each," = ",result)
        start = result
    return
        

def Check_Not_Flaot(arg):
    wrong_letters = arg
    for each in arg:
        try:
            wrong_letters.remove(each)
        except: 
            continue
    return wrong_letters

def Eingabe():
    while True:
        temp = input("please input any numbers: ").split(",")
        try:
            numbers = list(map(float,temp))
            return numbers
        except:
            print("invalid number input: ",list(map(Check_Not_Flaot,temp))) 
            continue

print("calculator input code:")
print("multiplication   :1")
print("division         :2")
print("subtraction      :3")
print("addition         :4")  

while True:
    try:
        choice = int(input("your mode: "))
    
        if choice in range(1,6):
            print("form is: seperate with ',' whitespaces are ignored")
            print("example: 1, 3.14,-2048")
            if choice == 1:
                multiply(Eingabe())
            elif choice == 2:
                divide(Eingabe())
            elif choice == 3:
                subtract(Eingabe())
            elif choice == 4:
                add(Eingabe())
            elif choice == 5:
                power(Eingabe())
        else:
            print("invalid input")
    except:
        print("invalid input")