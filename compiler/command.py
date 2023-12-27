import os

import compiler.functions
from memory import Memory


class CommandHandler:
    def __init__(self, entry_point: str, mem: Memory):
        self.memory = mem
        self.start_pos = self.memory.get_memindex(entry_point)

    def start(self) -> int:
        i = self.start_pos
        while i < len(self.memory.mem):
            c = self.memory.mem[i]
            if c == 0xFF and self.memory.mem[i+1] == 0xFF:
                return 0
            try:
                goto = compiler.functions.commands[c][1](i, self.memory)
            except KeyError:
                raise KeyError(f'No Command with opcode {c:08b}, location: {i}')
            if goto == -1:
                i += 1
            else:
                i = goto
        return 1

class Runner:
    def __init__(self, file: str, entry_point: int):
        self.filepath = file
        self.entry = entry_point

    def load(self) -> Memory:
        mem = Memory(os.path.getsize(self.filepath), self.filepath)
        return mem

    def run(self, mem: Memory):
        mem.labels[(entry_label := '.entry312432sa')] = self.entry
        handler = CommandHandler(entry_label, mem)
        handler.start()
        pass
