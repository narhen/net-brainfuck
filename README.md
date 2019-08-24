# net-brainfuck
An extension to the [brainfuck](https://en.wikipedia.org/wiki/Brainfuck) language enabling networked communication.
Inspired by [Socket extensions for esoteric languages](https://pdfs.semanticscholar.org/e9ad/2d385a5f6626a80f73aa14e6b6b2a36ff79e.pdf).

# Example
The [sock.bf](sock.bf) program will set up a TCP server listening on port 1025.
When a client connects it sends "A\n" then exits.

### Terminal 1:
```bash
$ ./main.py sock.bf
```

### Terminal 2:
```bash
$ nc 0 1025
A

```
