
from push_message import push_message
import time

S = time.time()

for i in range(10):
    push_message()
    if i < 10:
        time.sleep(60)

E = time.time()
print(E-S)

