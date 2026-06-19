import json
from enum import Enum
class Component(str, Enum):
    SECURITY = 'security'

try:
    print(json.dumps({'component': Component.SECURITY}))
except Exception as e:
    print('Failed:', repr(e))
