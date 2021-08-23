from enum import Enum

class Module:
    _instance = None
    _module = None
    def __new__(class_, *args, **kwargs):
        if class_._instance is None:
            class_._instance = super().__new__(class_)
        return class_._instance

    def __init__(self, module=None):
        if module is not None:
            self._module = module


class ModuleEnum(Enum):
    Deamon = 0
    Client = 1