import struct
import typing

from memory import Memory
import memory


def test1(location: int, mem: Memory):
    print("hello stupid")
    return -1


def test2(location: int, mem: Memory):
    print("test2")
    return -1

def print_s(location: int, mem: Memory):
    str_location = mem.get_int(location+1)
    memory.printi(str_location, mem)

    return location+5

def test3(location: int, mem: Memory):
    print('test 3')
    return -1

def jump(location: int, mem: Memory):
    goto = mem.get_int(location+1)
    return goto

def print_m(location: int, mem: Memory):
    memory_location = mem.get_int(location+1)
    value = mem.get_i(memory_location)
    print(value, end='')
    return location+5

def print_i(location: int, mem: Memory):
    memory_location = mem.get_int(location+1)
    value = mem.get_int(memory_location)
    print(value, end='')
    return location+5

def print_cptr(location: int, mem: Memory):
    char_ptr = mem.get_int(location+1)
    char = chr(mem.get_i(char_ptr))
    print(char, end='')
    return location+5

def print_c(location: int, mem: Memory):
    char = chr(mem.get_int(location+1))
    print(char, end='')
    return location+5

def is_string(mem, location):
    try:
        offset = 0
        while True:
            char: bytes = struct.pack('B', mem.get_i(location+offset))
            if not char or char == b'\x03':
                break
            char.decode('utf-8')  # Try decoding each byte as UTF-8
        return True
    except UnicodeDecodeError:
        return False

def skip(location: int, _):
    return location+2

def seti(location: int, mem: Memory):
    second_is_pointer = True if mem.get_i(location+1) == 1 else False
    location1 = mem.get_int(location+2)
    v2 = mem.get_int(location+6)
    if second_is_pointer:
        v2 = mem.get_int(v2)
    mem.set_int(location1, [v2])
    return location+10

def setb(location: int, mem: Memory):
    second_is_pointer = True if mem.get_i(location+1) == 1 else False
    location1 = mem.get_int(location+2)
    v2 = mem.get_int(location+6)
    if second_is_pointer:
        v2 = mem.get_i(v2)
    mem.set(location1, struct.pack('>B', v2))
    return location+10

def compare(location: int, mem: Memory):
    location1 = mem.get_int(location+1)
    if is_string(mem, location+5):
        srtingA = mem.get_str(location1)
        stringB = mem.get_str(location+5)

    return location+5

def sets(location: int, mem: Memory):
    second_is_pointer = True if mem.get_i(location+1) == 1 else False
    location1 = mem.get_int(location+2)
    v2 = ""
    if second_is_pointer:
        v2 = mem.get_str(mem.get_int(location+6))
        mem.set_string(location1, [v2])
        return location + 10
    else:
        v2 = mem.get_str(location+6)
        mem.set_string(location1, [v2])
        return location + 6 + len(v2) + 1


commands: dict[int, typing.Tuple[str, typing.Callable[[int, Memory], int]]] = {
    0b00000101: ('test1', test1),
    0b00000110: ('test2', test2),
    0b00000111: ('test3', test3),
    0b00000001: ('skip', skip),
    0b00001000: ('print', print_s),
    0b00001001: ('printp', print_m),
    0b00001011: ('printi', print_i),
    0b00001010: ('printc', print_c),
    0b00001100: ('print_cptr', print_cptr),
    0b00000010: ('jmp', jump),
    0b00010000: ('setb', setb),
    0b00010001: ('seti', seti),
    0b00010010: ('sets', sets),
    0b00100001: ('cmp', compare)
}
