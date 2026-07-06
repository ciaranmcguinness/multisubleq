import abc
from blessed import Terminal, keyboard

class IO(abc.ABC):
    def get(self) -> int:
        raise NotImplemented
    
    def set(self, i):
        raise NotImplemented
    
    def has_val(self) -> bool:
        raise NotImplemented
    
class TextIO(IO):
    def __init__(self, color):
        self.term = Terminal()
        self.keys: list[int] = []
        self.color = color

    def get(self) -> int:
        if len(self.keys) == 0:
            return 0
        else:
            code = self.keys.pop()
            return code

    def set(self, i: int):
        print(self.term.color_rgb(self.color,255,255)(chr(i)),end="", flush=True)

    def has_val(self) -> bool:
        return len(self.keys) != 0

class IntIO(IO):
    def get(self):
        return int(input(">"))
    def set(self, i):
        print(i)
    def has_val(self) -> bool:
        return input("have val?") == "y"
    
class Head():
    def __init__(self, code: list[int], ios: list[IO]):
        self.code = code.copy()
        self.ios = ios
        if len(code) == 0:
            raise Exception()
        self.ip = 0
        self.id = 0

    def iti(self, i):
        return self.ios[((i * -1) -1) % len(self.ios)]
    
    def gwr(self, i):
        return self.code[i % len(self.code)]

    def advance(self):
        if self.ip >= 0:
            a = self.gwr(self.ip)
            b = self.gwr(self.ip + 1)
            c = self.gwr(self.ip + 2)
            match (int(a < 0) + (int(b<0) * 2)):
                case 0: 
                    self.code[b % len(self.code)] -= self.gwr(a)
                    if self.gwr(b) > 0:
                        c = self.ip + 3
                case 1:
                    self.code[b % len(self.code)] -= self.iti(a).get()
                    if self.gwr(b) > 0:
                        c = self.ip + 3
                case 2:
                    self.iti(b).set(self.gwr(a))
                case 3:
                    self.iti(b).set(self.iti(a).get())
                case _:
                    raise Exception("Shouldnt be possible")
            self.ip = c
        else:
            if ((self.ip * -1) -1) < len(self.ios):
                if self.ios[((self.ip * -1) -1)].has_val():
                    self.ip = 0

def asm(inp: str):
    procinp = list(filter(lambda l: len(l) != 0, " ".join(filter(lambda l: l[0] != "#", filter(lambda x: len(x) != 0, map(lambda x: x.split("#")[0], inp.split("\n"))))).split(" ")))
    print(procinp)
    keys = {}
    c = []
    highest = 0
    for i, v in enumerate(procinp):
        if v[0] == "h":
            highest = max(int(v[1:]) + 1, highest)
        s = v.split(":")
        if len(s) == 2:
            #print(f"adding {s[0]}")
            keys[s[0]] = str(i)
            procinp[i] = s[1]
    for i, v in enumerate(procinp):
        w = v.replace("?",str(i)).replace("h",f"{len(procinp)}+")
        for k, val in keys.items():
            if w == k:
                w = val
        c.append(eval(w))
    c.extend([0 for _ in range(highest)])
    return c

def fmtprint(c, s:str=""):
    procs = None
    if s != "":
        procs = " ".join(filter(lambda l: l[0] != "#", s.split("\n"))).split(" ")
    else:
        procs = []
    for i, v in enumerate(c):
        if i < len(procs):
            print(f"{i}({procs[i]}):{v} ",end="")    
        else:
            print(f"{i}:{v} ",end="")
        if ((i + 1) % 3) == 0:
            print()
    print()

def main():
    inp = """# Output the character pointed to by p.
a a ?+1
p Z ?+1
Z a ?+1
Z Z ?+1
a:0 -1 ?+1

# Increment p.
m1 p ?+1

# Check if p < E.
a a ?+1
E Z ?+1
Z a ?+1
Z Z ?+1
p a -1

Z Z 0

p:H Z:0 m1:-1

# Our text "Hello, world!" in ASCII codes
H:72 101 108
108 111 44
32 87 111
114 108 100
33 10 E:E"""
    c = asm(inp)
    fmtprint(c)
    tio = TextIO(0)
    h = Head(c, [tio])
    h.ip = 0
    while True:
        #if h.ip >= 0:
            #print(h.code, h.ip)
        #    h.advance()
        #    print(h.code, h.ip)
        #else:
        #    h.advance()
        h.advance()
        #print(tio.keys)
        with tio.term.cbreak():
            x = ""
            if h.ip < 0: 
                x = tio.term.inkey(0.1)
            else:
                pass
                #x = tio.term.inkey(0.005)
            if len(x) == 1:
                tio.keys.append(ord(x))
            #if x != None:
            #    print(x)
            #    tio.keys.append(x)


if __name__ == "__main__":
    main()
