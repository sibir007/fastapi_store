
from time import sleep

from project.mod2 import fun2


fun2()

def fun3():
    print('in fun3')
    while True:
        s = 10
        sleep(s)
        print(f'in sleep {s}')


fun3()


