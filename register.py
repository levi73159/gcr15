class Flags:
    def __init__(self, id_: int, bits: list[bool]):
        self.id = id_
        self.bits = bits

    def __getitem__(self, item):
        return self.bits[item]

    def __setitem__(self, key, value):
        self.bits[key] = value


class Register:
    def __init__(self, id_: int, value: int):
        self.id = id_
        self.value = value
