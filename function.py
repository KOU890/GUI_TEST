import time

def loop1(bool):
    int = 0
    while bool == True:
        print(int)
        int += 1
        time.sleep(1)

def change_bool():
    bool = False
    return(bool)