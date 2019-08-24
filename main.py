#!/usr/bin/env python3

import sys
import os

class BFState():
    class Braces():
        def __init__(self, start, end):
            self.start = start
            self.end = end

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return f"(start={self.start}, end={self.end})"

    def __init__(self, program, tape_size=1024):
        self.tape_idx = 0
        self.tape = [0]*tape_size

        self.ip = 0
        self.program = program

        self.braces = []

        self.commands = {
            ">": self.increment_idx,
            "<": self.decrement_idx,
            "+": self.increment_value,
            "-": self.decrement_value,
            ".": self.write,
            ",": self.read,
            "[": self.left_brace,
            "]": self.right_brace
        }

    def __repr__(self):
        return f"""{self.program}
{' '*self.ip}^ ({self.ip})
tape idx    = {self.tape_idx}
data        = {self.data}
loops       = {self.braces}
"""

    def is_finished(self):
        return self.ip >= len(self.program)

    def execute(self, debug=False):
        while not self.is_finished():
            if debug:
                print(self)
                if input():
                    import IPython; IPython.embed()

            self.next()

    def next(self):
        """Execute instruction at current IP, then increment IP
           Returns True if program is finished, False otherwise"""
        if self.is_finished():
            return

        while self.instruction not in self.commands:
            self.ip += 1

        if self.is_finished():
            return

        self.commands[self.instruction]()
        self.ip += 1

    @property
    def instruction(self):
        return self.program[self.ip]

    @property
    def data(self):
        return self.tape[self.tape_idx]

    def increment_idx(self):
        self.tape_idx += 1

        if self.tape_idx >= len(self.tape):
            self.tape = self.tape + [0]*1024

    def decrement_idx(self):
        self.tape_idx -= 1

        if self.tape_idx < 0:
            to_increment = 1024
            self.tape = [0]*to_increment + self.tape
            self.tape_idx += to_increment

    def increment_value(self):
        self.tape[self.tape_idx] += 1

    def decrement_value(self):
        self.tape[self.tape_idx] -= 1

    def write(self):
        os.write(sys.stdout.fileno(), chr(self.tape[self.tape_idx]).encode())

    def read(self):
        self.tape[self.tape_idx] = os.read(sys.stdin.fileno(), 1)

    def _get_matching_right_brace(self):
        if self.program[self.ip] != "[":
            raise Exception("No brace at current IP")

        if len(self.braces) > 0 and self.braces[-1].start == self.ip:
            return self.braces.pop()

        depth = len(self.braces)
        end_ip = self.ip
        while True:
            if self.program[end_ip] == "[":
                depth += 1
            elif self.program[end_ip] == "]":
                depth -= 1
                if depth == len(self.braces):
                    break

            end_ip += 1
            if end_ip >= len(self.program):
                raise Exception("Found left brace but no matching right brace")

        return BFState.Braces(self.ip, end_ip)

    def left_brace(self):
        braces = self._get_matching_right_brace()
        if self.data != 0:
            self.braces.append(braces)
        else:
            self.ip = braces.end

    def right_brace(self):
        if len(self.braces) == 0:
            raise Exception("Found right brace but no matching left brace")

        if self.data == 0:
            self.braces.pop()
        else:
            self.ip = self.braces[-1].start - 1

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <brainfuck program file>")
        return 1

    program = open(sys.argv[1]).read().replace("\n", " ")
    BFState(program).execute(len(sys.argv) > 2)

if __name__ == '__main__':
    sys.exit(main())
