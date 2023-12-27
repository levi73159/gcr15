import os.path
import struct

from memory import Memory, is_byte, is_integer, is_string_pointer
import typing
from compiler import functions


class Parser:
    def __init__(self, out_file: str, in_file: str, size: int):
        self.in_ = in_file
        self.out = out_file
        self.size = size
        self.pointers: dict[str, int] = dict()
        self.defines: dict[str, str] = dict()

    def parse(self, author):
        # Pre-allocate the file with empty bytes
        with open(self.out, 'wb') as f:
            f.write(bytes([0] * self.size))

        mem = Memory(self.size, self.out)
        mem.var_str("TAG", "GCR15")
        mem.var_bytes("DATA", bytes([32, 12, 65, 32]))
        if author:
            mem.var_str("AUTHOR", author)

        with open(self.in_, 'r') as f:
            code_lines = f.readlines()

        # Write the parsed bytecode to the file
        with open(self.out, 'r+b') as f:
            for line in code_lines:
                if line.isspace() or not line:
                    continue
                opcode, args = self.parse_line(line.strip(), f)
                if opcode == -1:
                    f.seek(int(args[0], 0), 0)
                    continue
                if opcode == -2:
                    continue
                f.write(struct.pack('>B', opcode))  # Write the opcode as a single byte
                for arg in args:
                    f.write(self.parse_arg(arg))

            # Add two bytes with the maximum value to mark the end of code
            f.write(struct.pack('>H', 0xFFFF))

    def parse_arg(self, arg: str, default: str = '<I') -> bytes:
        if arg.startswith('['):
            ptr_name = arg.removeprefix('[').removesuffix(']')
            return struct.pack('<I', self.pointers[ptr_name])

        if arg.startswith('"') and arg.endswith('"'):
            # Process escape characters and remove quotes
            processed_arg = bytes(arg.encode('utf-8').decode('unicode_escape'), 'utf-8')[1:-1]
            return processed_arg

        return struct.pack(default, int(arg, 0))  # Write each argument as a 4-byte integer

    def get_opcode(self, cmd_name: str):
        for opcode, (name, _) in functions.commands.items():
            if cmd_name == name:
                return opcode
        raise Exception(f"There is no command named: {cmd_name}")

    def allocate(self, cmd_name, parsed_args: list[str], file):
        if cmd_name == 'malc':
            for arg in parsed_args:
                file.write(self.parse_arg(arg))
            return True
        if cmd_name == 'malcb':
            for arg in parsed_args:
                file.write(self.parse_arg(arg, '>B'))
            return True
        if cmd_name == 'malcs':
            size = int(parsed_args[0], 0)
            value = parsed_args[1]
            for _ in range(size):
                file.write(struct.pack('>B', int(value, 0)))
            return True
        return False

    def set_memory(self, cmd_name, parsed_args: list[str], file):
        if cmd_name == 'set':
            if parsed_args[1].startswith('"'):
                self.write_opcode(file, 'sets')
                return 0, parsed_args
            elif is_byte(parsed_args[1]):
                self.write_opcode(file, 'setb')
                return 0, parsed_args
            elif is_integer(parsed_args[1]):
                self.write_opcode(file, 'seti')
                return 0, parsed_args
            else:
                # must be a pointer
                ptr = self.pointers[parsed_args[1].lstrip('[').rstrip(']')]
                parsed_args[1] = str(ptr)
                if is_string_pointer(ptr, file):
                    self.write_opcode(file, 'sets')
                    return 1, parsed_args
                else:
                    opcode = self.get_opcode('seti')
                    file.write(struct.pack('>B', opcode))
                    return 1, parsed_args
        elif cmd_name == 'sets':
            if parsed_args[1].startswith('"'):
                self.write_opcode(file, 'sets')
                return 0, parsed_args
            else:
                ptr = self.pointers[parsed_args[1].lstrip('[').rstrip(']')]
                parsed_args[1] = str(ptr)
                self.write_opcode(file, 'sets')
                return 1, parsed_args
        elif cmd_name == 'setb':
            if is_byte(parsed_args[1]):
                self.write_opcode(file, 'setb')
                return 0, parsed_args
            else:
                ptr = self.pointers[parsed_args[1].lstrip('[').rstrip(']')]
                parsed_args[1] = str(ptr)
                self.write_opcode(file, 'setb')
                return 1, parsed_args
        elif cmd_name == 'seti':
            if is_integer(parsed_args[1]):
                self.write_opcode(file, 'seti')
                return 0, parsed_args
            else:
                ptr = self.pointers[parsed_args[1].lstrip('[').rstrip(']')]
                parsed_args[1] = str(ptr)
                self.write_opcode(file, 'seti')
                return 1, parsed_args
        return -2, []

    def parse_line(self, line: str, file: typing.BinaryIO):
        if ';' in line:
            # Remove everything after the semicolon, treating it as a comment
            line = line.split(';', 1)[0].strip()
        line = self.add_labels(file, line)
        if not line or line.isspace():
            return -2, []

        for key, value in self.defines.items():
            line = line.replace(key, value)

        spl = line.split(' ')
        cmd_name, args = spl[0], spl[1:]
        if cmd_name == 'define':
            define_name = args[0]
            define = ' '.join(args[1:])
            self.defines[define_name] = define
            return -2, []
        if cmd_name == 'org':
            return -1, args

        parsed_args = []
        current_arg = ''
        in_string = False

        parsed_args = self.process_args(args, current_arg, in_string, parsed_args)

        if self.allocate(cmd_name, parsed_args, file):
            return -2, []

        tmp_opcode, pa = self.set_memory(cmd_name, parsed_args, file)
        if tmp_opcode != -2:
            return tmp_opcode, pa

        opcode = self.get_opcode(cmd_name)
        return opcode, parsed_args

    def process_args(self, args, current_arg, in_string, parsed_args):
        for arg in args:
            if arg.startswith('"') and not in_string:
                current_arg += arg + ' '
                in_string = True
            elif arg.endswith('"') and in_string:
                current_arg += arg
                parsed_args.append(current_arg)
                current_arg = ''
                in_string = False
            elif in_string:
                current_arg += arg + ' '
            else:
                parsed_args.append(arg)
        if current_arg and in_string:
            parsed_args.append(current_arg.strip())
        return parsed_args

    def add_labels(self, file, line):
        if ':' in line:
            spl = line.split(':')
            label = spl[0]
            self.pointers[label] = file.tell()
            line = line.removeprefix(spl[0] + ':').strip()
        return line

    def write_opcode(self, file, name):
        if not name:
            opcode = 0
        else:
            opcode = self.get_opcode(name)
        file.write(struct.pack('>B', opcode))

