import sys
import struct
import typing


class Memory:
    def __init__(self, storage: int = 1_000, file: str | None = None):
        self.mem = bytearray(struct.pack('B' * storage, *([0] * storage)))
        self.labels: dict[str, int] = dict()
        self.file = file
        if file:
            with open(file, 'rb') as f:
                file_contents = f.read(storage)
                self.mem[:len(file_contents)] = file_contents

    def get(self, label: str) -> int:
        return self.mem[self.labels[label]]

    def get_memindex(self, label: str) -> int:
        return self.labels[label]

    def get_i(self, index: int) -> int:
        return self.mem[index]

    def set(self, index: int, values: bytes):
        for offset, v in enumerate(values):
            i = index + offset
            self.mem[i] = v
            self.update(i, v)

    def get_int(self, index: int) -> int:
        # Assuming a 4-byte (32-bit) integer in little-endian format
        return struct.unpack('<I', bytes(self.mem[index:index + 4]))[0]

    def get_str(self, index: int) -> str:
        str_bytes = bytearray()
        while self.mem[index] != 3:  # Assuming the end marker is 3
            str_bytes.append(self.mem[index])
            index += 1
        return str(str_bytes, 'utf-8')

    def set_int(self, index: int, values: list[int]):
        for offset, v in enumerate(values):
            i = index + (offset * 4)  # 4 bytes per int
            vs = struct.pack('<I', v)
            self.mem[i:i + 4] = vs
            self.update(i, v, '<I')

    def update(self, location: int, v: int, format_: str = '>B'):
        if self.file is None: return
        with open(self.file, 'r+b') as f:
            f.seek(location, 0)
            f.write(struct.pack(format_, v))

    def var_str(self, name: str, value: str) -> int:
        location = self.find_free_memory(len(value)+1)
        self.labels[name] = location
        self.set_string(location, [value])
        return location

    def var_bytes(self, name: str, value: bytes) -> int:
        location = self.find_free_memory(len(value))
        self.labels[name] = location
        self.setl(name, value)
        return location

    def find_free_memory(self, size: int = 0) -> int:
            """
            Find a contiguous block of free memory with the specified size.

            Parameters:
            - size (int): The size of the desired memory block.

            Returns:
            - int: The starting index of the free memory block if found, or -1 if not found.
            """
            free_memory_start = -1
            current_block_size = 0

            for i, value in enumerate(self.mem):
                if value == 0:
                    # Found a free memory cell
                    if current_block_size == 0:
                        free_memory_start = i
                    current_block_size += 1

                    # Check if we've found enough free memory
                    if current_block_size == size:
                        return free_memory_start

                else:
                    # Reset block size counter if we encounter a non-free cell
                    current_block_size = 0

            return -1  # Not enough free memory found

    def set_string(self, index: int, values: list[str]):
        for value in values:
            i: int = 0
            for offset, char in enumerate(value):
                i = index + offset
                # Convert each character to its ASCII value
                self.mem[i] = ord(char)
                self.update(i, ord(char))
            self.mem[i+1] = 3
            self.update(i+1, 3)
            index = i+2

    def setl(self, label: str, values: bytes):
        index = self.labels[label]
        for offset, v in enumerate(values):
            i = index + offset
            self.mem[i] = v
            self.update(i, v)

def prints(label: str, mem: Memory):
    for i in mem.mem[mem.get_memindex(label):]:
        if i == 3:
            break
        print(chr(i), end='')

def printi(loc: int, mem: Memory):
    for i in mem.mem[loc:]:
        if i == 3:
            break
        print(chr(i), end='')

def is_byte(value: str) -> bool:
    try:
        byte_value = int(value)
        return 0 <= byte_value <= 255
    except ValueError:
        return False

def is_integer(value: str) -> bool:
    return value.isdigit()

def is_string_pointer(pointer: int, file: typing.BinaryIO) -> bool:
    old = file.tell()
    try:
        file.seek(pointer, 0)
        while True:
            char = file.read(1)
            if not char or char == b'\x03':
                break
            char.decode('utf-8')  # Try decoding each byte as UTF-8
        file.seek(old, 0)
        return True
    except UnicodeDecodeError:
        file.seek(old, 0)
        return False