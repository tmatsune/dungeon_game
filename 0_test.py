
from heapq import heapify, heappush, heappop

class Dog():
    def __init__(self) -> None:
        self.type = 'dog'

dog = Dog()
if isinstance(dog, Dog): print('is doh')
else: print('not dog')



tests ={
    1: '1',
    2: '2',
    3: '3',
}

for i, k in tests.items():
    print(i, k)