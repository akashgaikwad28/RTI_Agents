from enum import Enum
class C(str, Enum):
    S = 'security'

print(C.S == 'security')
