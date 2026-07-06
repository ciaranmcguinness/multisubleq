import abc
from blessed import Terminal, keyboard
import argparse
from multi import run_dualcore
from helpers import asm

if __name__ == "__main__":
    p = argparse.ArgumentParser("MultiSubleq",description="An interpreter for MultiSubleq.")
    p.add_argument("asm1", type=argparse.FileType("r"))
    p.add_argument("asm2", type=argparse.FileType("r"))
    p.add_argument("--boost", type=int, default=32, help="How many clock cycles per reading of input. (You probably don't need to touch this.)")
    a = p.parse_args()
    print("Assembling the code for core 1!")
    c1 = asm(a.asm1.read())
    print("Assembling the code for core 2!")
    c2 = asm(a.asm2.read())
    run_dualcore(c1, c2, a.boost)
