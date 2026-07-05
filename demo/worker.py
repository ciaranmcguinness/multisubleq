from pyscript import web, when # type: ignore
import asyncio
import abc

print("Loaded!")

class IO(abc.ABC):
    def get(self) -> int:
        raise NotImplemented
    
    def set(self, i: int):
        raise NotImplemented
    
    def has_val(self) -> bool:
        raise NotImplemented
    
class HTMLIO(IO):
    def __init__(self, inpid, outid):
        self.inp = web.page[inpid]
        self.out = web.page[outid]

    def get(self) -> int:
        print("getting...")
        if len(self.inp.value) != 0:
            v = self.inp.value[0]
            self.inp.value = self.inp.value[1:]
            print(v)
            print(self.inp.value)
            return ord(v)
        return 0

    def set(self, i:int):
        print("setting...")
        print(i)
        o = (chr(i).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br>"))
        self.out.innerHTML += o

    def has_val(self):
        return len(self.inp.value) != 0

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
            val = int(a < 0) + (int(b<0) * 2)
            if val == 0: 
                self.code[b % len(self.code)] -= self.gwr(a)
                if self.gwr(b) > 0:
                    c = self.ip + 3
            elif val == 1:
                self.code[b % len(self.code)] -= self.iti(a).get()
                if self.gwr(b) > 0:
                    c = self.ip + 3
            elif val == 2:
                self.iti(b).set(self.gwr(a))
            elif val == 3:
                self.iti(b).set(self.iti(a).get())
            self.ip = c
        else:
            if self.ios[((self.ip * -1) -1)].has_val():
                self.ip = 0

class Reg(IO):
    def __init__(self):
        self.vals = []

    def get(self) -> int:
        if len(self.vals) == 0:
            return 0
        else:
            return self.vals.pop()
    
    def set(self, i):
        self.vals.append(i)

    def has_val(self) -> bool:
        return len(self.vals) != 0
    
def pair():
    a = Reg()
    b = Reg()
    aset = a.set
    a.set = b.set
    b.set = aset
    return (a, b)

def asm(inp: str) -> list[int]:
    prep = inp.split("\n")
    for i in range(0,len(prep)):
        prep[i] = prep[i].split("#")[0]
    prep = (" ".join(prep)).split(" ")
    procinp = [] #for some reason, micropython hates my filter statements, so i have to do THIS.
    for i in range(0, len(prep)):
        if prep[i] != "":
            procinp.append(prep[i])
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

running = False

jmp = False


print("here")

@when("click", "#rstart")
async def res(e):
    global jmp
    jmp = True
    web.page["output1"].innerHTML = '<span class="placeholder">&gt;&gt;&gt; waiting to start...</span><br>'
    web.page["output2"].innerHTML = '<span class="placeholder">&gt;&gt;&gt; waiting to start...</span><br>'

@when("click", "#run")
async def run(e):
    print("run!")
    global running
    running = not running

while True:
    web.page["p1stat"].innerHTML = "Stopped"
    web.page["p2stat"].innerHTML = "Stopped"
    web.page["output1"].innerHTML = '<span class="placeholder">&gt;&gt;&gt; waiting to start...</span><br>'
    web.page["output2"].innerHTML = '<span class="placeholder">&gt;&gt;&gt; waiting to start...</span><br>'
    if running:
        p = pair()
        proc1 = None
        code1 = web.page["dev1"].value
        if len(code1) != 0:
            proc1 = Head(asm(code1), [HTMLIO("input1","output1"),p[0]])
        proc2 = None
        code2 = web.page["dev2"].value
        if len(code2) != 0:
            proc2 = Head(asm(code2), [p[1],HTMLIO("input2","output2")])
        i = 0
        print("Inited!")
        while running:
            r = False
            if jmp:
                jmp = False
                break
            if proc1 != None:
                proc1.advance()
                if proc1.ip >= 0:
                    r = True
                    web.page["p1stat"].innerHTML = "Running"
                else:
                    wid = (proc1.ip * -1) -1
                    if wid >= len(proc1.ios):
                        web.page["p1stat"].innerHTML = "Stopped"
                        proc1 = None
                    else:
                        web.page["p1stat"].innerHTML = f"Waiting for value on device {wid}"
            if proc2 != None:
                proc2.advance()
                if proc2.ip >= 0:
                    r = True
                    web.page["p2stat"].innerHTML = "Running"
                else:
                    wid = (proc2.ip * -1) -1
                    if wid >= len(proc2.ios):
                        web.page["p2stat"].innerHTML = "Stopped"
                        proc2 = None
                    else:
                        web.page["p2stat"].innerHTML = f"Waiting for value on device {wid}"
            if r:
                if i >= 250:
                    await asyncio.sleep(0.001)
                    i = 0
                i += 1
            else:
                await asyncio.sleep(0.1)
    else:
        await asyncio.sleep(0.5)