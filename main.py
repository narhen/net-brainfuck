#!/usr/bin/env python3

import sys
import os
import socket

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
        self.commands = {}

        self.add_command(">", self.increment_idx)
        self.add_command("<", self.decrement_idx)
        self.add_command("+", self.increment_value)
        self.add_command("-", self.decrement_value)
        self.add_command(".", self.write)
        self.add_command(",", self.read)
        self.add_command("[", self.left_brace)
        self.add_command("]", self.right_brace)

    def __repr__(self):
        return f"""{self.program}
{' '*self.ip}^ ({self.ip})
tape idx    = {self.tape_idx}
data        = {self.data}
loops       = {self.braces}
"""

    def add_command(self, instruction, callback):
        self.commands[instruction] = callback

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
    def data(self, idx=None):
        if not idx:
            idx = self.tape_idx
        return self.tape[idx]

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

class NetBrainFuck(BFState):
    def __init__(self, program):
        super().__init__(program)
        self.add_command("@", self.socket_op)
        self.add_command("!", self.debug)

        self.sockets = {}
        self.sock_commands = {
            0: self.create_and_bind,
            1: self.listen,
            2: self.accept,
            3: self.sock_read,
            4: self.sock_write,
         }


    @property
    def case_byte(self):
        return self.tape[self.tape_idx + 1]

    def socket_op(self):
        if self.case_byte not in self.sock_commands:
            return

        print(self.sock_commands[self.case_byte].__name__)
        self.sock_commands[self.case_byte]()

    def get_port(self):
        b1, b2 = self.tape[self.tape_idx + 2: self.tape_idx + 4]
        return b1 | (b2 << 8)

    def get_socket(self, idx):
        return self.sockets[self.tape[idx]]

    def get_ip_addr(self):
        b1, b2, b3, b4 = self.tape[self.tape_idx + 4: self.tape_idx + 8]
        return f"{b4}.{b3}.{b2}.{b1}"


    # tape index + 0: where the filedescriptor will be stored
    # tape index + 2: lower byte of the port number
    # tape index + 3: upper byte of the port number
    # tape index + 4: lowest byte of ip address
    # tape index + 5: second lowest byte of ip address
    # tape index + 6: second upper byte of ip address
    # tape index + 7: upper byte of ip address
    def create_and_bind(self):
        sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        host, port = self.get_ip_addr(), self.get_port()
        sd.bind((host, port))

        self.sockets[sd.fileno()] = sd
        self.tape[self.tape_idx] = sd.fileno()

    # socket fd must be at tape index + 2
    def listen(self):
        sd = self.get_socket(self.tape_idx + 2)
        sd.listen()

    # socket fd must be at tape index + 2
    # client fd will be stored at tape index
    def accept(self):
        sd = self.get_socket(self.tape_idx + 2)

        csd, addr = sd.accept()
        self.tape[self.tape_idx] = csd.fileno()
        self.sockets[csd.fileno()] = csd

    # socket fd must be at tape index + 2
    # read byte will be stored at tape index
    def sock_read(self):
        sd = self.get_socket(self.tape_idx + 2)
        self.tape[self.tape_idx] = sd.recv(1)

    # socket fd must be at tape index + 2
    # write byte stored at tape index
    def sock_write(self):
        sd = self.get_socket(self.tape_idx + 2)
        sd.send(chr(self.data).encode())

    def debug(self):
        import IPython; IPython.embed()

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <brainfuck program file>")
        return 1

    program = open(sys.argv[1]).read().replace("\n", " ")
    NetBrainFuck(program).execute(len(sys.argv) > 2)

if __name__ == '__main__':
    sys.exit(main())
