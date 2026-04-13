
# import os
# import sys
from time import sleep

from project.mod2 import fun2


fun2()

def fun3():
    print('in fun3')
    while True:
        s = 10
        sleep(s)
        print(f'in sleep {s}')


# fun3()

# for ev in os.environ:
#     print(f'{ev}: {os.environ[ev]}')


from project.config import settings

ss = settings.model_dump_json(indent=4)

print(ss)
print(f'POSTGRES_URL: {settings.POSTGRES_URL}')
print(f'REDIS_URL: {settings.REDIS_URL}')