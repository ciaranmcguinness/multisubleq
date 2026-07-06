import abc

class IO(abc.ABC):
    def get(self) -> int:
        raise NotImplemented
    
    def set(self, i):
        raise NotImplemented
    
    def has_val(self) -> bool:
        raise NotImplemented


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