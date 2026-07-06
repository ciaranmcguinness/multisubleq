from main import Head, IntIO, asm, IO, fmtprint, TextIO
import blessed
import time

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

class Compiler():
    def __init__(self):
        self.code = "Z:Z Z interupt:?+1\n"
        self.heapi = 0
        self.tagi = 0
        self.locali = 0
        self.consts = []
        self.interupt = "interupt"
        self.addh = self.heap()
        self.geqh = self.heap()
        self.panic = self.get_tag()
        self.one = self.const(1)

    def heap(self):
        self.heapi += 1
        return f"h{self.heapi -1}"
    
    def const(self, v):
        self.consts.append(v)
        return f"c{len(self.consts) -1}"
    
    def get_tag(self, name= None):
        if name != None:
            self.comment(f"tag {name} = t{self.tagi}")
        self.tagi += 1
        return f"t{self.tagi -1}"
    
    def set_tag(self, tag):
        self.code += f"{tag}:"
    
    def sub(self, v1, v2):
        self.code += f"{v1} {v2} ?+1\n"
    
    def jump(self, t):
        self.code += f"Z Z {t}\n"
    
    def clear(self, v):
        self.code += f"{v} {v} ?+1\n"

    def add(self, v1, v2):
        self.comment("begin add")
        self.clear(self.addh)
        self.sub(v1, self.addh)
        self.sub(self.addh, v2)
        self.comment("end add")

    def subleq(self, v1, v2, t):
        self.code += f"{v1} {v2} {t}\n"

    def compile(self):
        self.set_tag(self.panic)
        self.print_str("Panic!", "-1")
        #self.sub(self.const(10101010101),"-1")
        self.jump(self.panic)
        for i, c in enumerate(self.consts):
            self.code += f"c{i}:{c} "
        return self.code
    
    def print_str(self, s:str, dev):
        consts = []
        for c in s:
            consts.append(self.const(ord(c)))
        for c in consts:
            self.sub(c, dev)
    
    def local(self):
        self.locali += 1
        return f"l{self.locali}"

    def geq(self, v1, v2, t):
        self.clear(self.geqh)
        self.add(v2, self.geqh)
        self.subleq(v1, self.geqh, t)

    def leq(self, v1, v2, t):
        self.geq(v2, v1, t)

    def leqz(self, v, t):
        self.subleq("Z", v, t)

    def lt(self, v1, v2, t):
        nxt = self.get_tag()
        done = self.get_tag()
        self.leq(v1,v2,nxt)
        self.jump(done)
        self.set_tag(nxt)
        self.geq(v1,v2,done)
        self.jump(t)
        self.set_tag(done)
        self.nop()

    def gt(self, v1, v2, t):
        nxt = self.get_tag()
        done = self.get_tag()
        self.geq(v1,v2,nxt)
        self.jump(done)
        self.set_tag(nxt)
        self.leq(v1,v2,done)
        self.jump(t)
        self.set_tag(done)
        self.nop()

    def mult(self, v1, v2):
        v2lt = self.get_tag()
        v2gt = self.get_tag()
        loop = self.get_tag()
        
        v1temp = self.heap()
        run = self.heap()
        acc = self.heap()
        self.clear(acc)
        self.clear(run)
        self.clear(v1temp)

        self.leqz(v2, v2lt)
        self.jump(v2gt)

        self.set_tag(v2lt)
        self.sub(v1, v1temp)
        self.sub(v2, run)
        self.jump(loop)

        self.set_tag(v2gt)
        self.add(v1, v1temp)
        self.add(v2, run)
        self.jump(loop)

        done = self.get_tag()

        self.set_tag(loop)
        self.leqz(run, done)
        self.sub(v1temp, acc)
        self.sub(self.one, run)
        self.jump(loop)
        self.set_tag(done)
        self.clear(v2)
        self.sub(acc, v2)

    def rev_mult(self, v1, v2):
        temp = self.heap()
        self.clear(temp)
        self.add(v2, temp)
        self.clear(v2)
        self.add(v1, v2)
        self.mult(temp, v2)

    def eq(self, v1, v2, target):
        n = self.get_tag()
        d = self.get_tag()
        self.geq(v1, v2, n)
        self.jump(d)
        self.set_tag(n)
        self.leq(v1,v2,target)
        self.set_tag(d)
        self.sub("Z","Z")

    def nop(self):
        self.sub("Z","Z")

    def neq(self, v1, v2, target):
        done = self.get_tag()
        self.eq(v1, v2, done)
        self.jump(target)
        self.set_tag(done)
        self.nop()

    def inv(self, v):
        o = self.heap()
        self.clear(o)
        self.sub(v, o)
        self.clear(v)
        self.add(o,v)

    def abs(self, v):
        o = self.heap()
        self.clear(o)
        done = self.get_tag()
        self.geq(v, "Z", done)
        self.sub(v, o)
        self.sub(v, o)
        self.set_tag(done)
        self.add(v, o)
        return o

    def comment(self, txt):
        if self.code[-1] != "\n":
            self.nop()
        self.code += f"#{txt}\n"

    def div(self, v1, v2): #I hate this function. it sucks all eggs in walmart. 
        n = self.heap()
        self.clear(n)
        self.add(self.one, n)

        v1t = self.abs(v1)
        v2t = self.abs(v2)
        count = self.heap()
        self.clear(count)
        self.sub(self.one, count)
        
        after1 = self.get_tag()
        after2 = self.get_tag()
        setm1 = self.get_tag()
        setp1 = self.get_tag()
        loop = self.get_tag()
        end = self.get_tag()

        self.eq(v1t, v1, after1)
        self.sub(self.one, n)
        self.set_tag(after1)
        self.sub("Z","Z")
        self.eq(v2t, v2, after2)
        self.sub(self.one, n)
        self.set_tag(after2)
        self.clear(v2)
        self.leqz(v1t, end)

        self.set_tag(loop)
        self.sub(v1t, v2t)
        self.add(self.one, count) 
        self.geq(v2t, "Z", loop)

        self.eq(n, "Z", setm1)

        self.set_tag(setp1)
        self.add(count, v2)
        self.jump(end)
        
        self.set_tag(setm1)
        self.sub(count, v2)

        self.set_tag(end)
        self.sub("Z","Z")


    def mod(self, v1, v2):
        m = self.heap()
        self.div_and_mod(v1, v2, m)
        self.clear(v2)
        self.add(m,v2)
        self.clear(m)

    def div_and_mod(self, divisor, res, rem):
        div_ltz = self.get_tag()
        div_not_ltz = self.get_tag()
        res_ltz = self.get_tag()
        res_not_ltz = self.get_tag()
        done = self.get_tag()

        m = self.heap()
        self.clear(m)

        self.lt(divisor, "Z", div_ltz)
        self.jump(div_not_ltz)
        self.set_tag(div_ltz)
        self.add(self.one, m)
        self.set_tag(div_not_ltz)

        self.lt(res, "Z", res_ltz)
        self.jump(res_not_ltz)
        self.set_tag(res_ltz)
        self.add(self.one, m)
        self.set_tag(res_not_ltz)

        self.rewrite(m,2,0)

        cpy = self.heap()
        self.clear(cpy)
        self.add(res, rem)

        self.div(divisor,res)
        self.add(res, cpy)
        self.mult(divisor, cpy)
        self.sub(cpy, rem)

        self.eq(rem,"Z",done)
        self.eq(m, "Z", done)
        self.add(divisor, rem)
        self.set_tag(done)

        self.nop()

    def jumptbl(self, v, targets):
        l = self.local()
        n = self.heap()
        p = self.heap()
        #reset code
        self.clear(p)
        self.sub(n, p)
        self.sub(p, l)
        self.sub(p, l)
        self.sub(p, l)
        self.clear(n)

        self.sub(v, n) #n = -v
        self.sub(n, l) #l += v
        self.sub(n, l) #l += v
        self.sub(n, l) #l += v
        self.code +=f"""Z Z {l}:?+1\n"""
        for tgt in targets:
            self.jump(tgt)

    def set_interupt(self, t):
        self.clear(self.interupt)
        self.add(self.const(t), self.interupt)

    def reset_interupt(self):
        self.clear(self.interupt)
        self.add(self.const(3), self.interupt)

    def get_int(self, dev, v):
        self.comment("begin get int")

        invalid_int = self.get_tag("invalid int")
        c = self.heap()
        tv = self.heap()
        loop = self.get_tag()
        done = self.get_tag()
        self.set_interupt(loop)

        self.set_tag(loop)
        self.clear(c)
        self.add(dev, c)
        self.eq(c, "Z", "-1")

        self.sub(c, dev)
        self.eq(c, self.const(10), done)

        self.sub(self.const(48), c)
        self.leq(c, self.const(-1), invalid_int)
        self.geq(c, self.const(10), invalid_int)

        self.clear(tv) #v *= 10
        self.add(v, tv)
        self.add(v, tv)
        self.clear(v)
        self.add(tv,v)
        self.add(tv,v)
        self.add(tv,v)
        self.add(tv,v)
        self.add(tv,v)

        self.add(c, v)
        self.jump(loop)
        self.set_tag(invalid_int)
        self.print_str("Invalid int!\n", "-1")
        self.clear(v)
        self.jump(loop)

        self.set_tag(done)
        self.reset_interupt()
        self.comment("end get int")

    def write_int(self, v, dev):
        cpy = self.heap()
        rev = self.heap()
        out = self.heap()
        self.clear(rev)
        self.add(self.one,rev)
        self.clear(cpy)
        self.add(v, cpy)
        skp = self.get_tag()
        self.geq(cpy, "Z", skp)
        self.sub(self.const(45), dev)
        self.inv(skp)
        self.set_tag(skp)
        self.nop()

        loop = self.get_tag()
        self.set_tag(loop)
        self.clear(out)
        self.div_and_mod(self.const(10), cpy, out)
        self.rev_mult(self.const(10),rev)
        self.add(out, rev)
        self.gt(cpy, "Z", loop)

        loop2 = self.get_tag()
        self.set_tag(loop2)
        self.clear(out)
        self.div_and_mod(self.const(10), rev, out)
        self.add(self.const(48),out)
        self.sub(out, dev)
        self.gt(rev, self.one, loop2)



    def rewrite(self, v, trigger:int, rew:int):
        done = self.get_tag()
        self.neq(v, self.const(trigger), done)
        self.clear(v)
        self.add(self.const(rew), v)
        self.set_tag(done)
        self.nop()


def piper_cpu1():
    comp = Compiler()

def piper_cpu2():
    comp = Compiler()


def fourfunc():
    comp = Compiler()
    acc = comp.heap()
    ch = comp.heap()
    inp = comp.heap()
    skip = comp.get_tag()
    skpval = comp.heap()

    invalid_symbol = comp.get_tag()
    add = comp.get_tag()
    sub = comp.get_tag()
    mult = comp.get_tag()
    div = comp.get_tag()
    mod = comp.get_tag()

    opts = [add, sub, mult, div, mod]
    tbl = comp.get_tag()
    comp.set_tag(tbl)
    comp.eq(skpval, comp.one, skip)
    comp.print_str("Current value: ", "-1")
    comp.write_int(acc, "-1")
    comp.sub(comp.const(10), "-1")
    comp.add(comp.one, skpval)
    comp.set_tag(skip)
    comp.clear(ch)
    comp.add("-1", ch)
    comp.eq(ch, 0, "-1")
    comp.sub(ch, "-1")
    comp.sub(comp.const(10), "-1")
    comp.rewrite(ch, 43, 0)
    comp.rewrite(ch, 45, 1)
    comp.rewrite(ch, 42, 2)
    comp.rewrite(ch, 47, 3)
    comp.rewrite(ch, 37, 4)
    comp.geq(ch, comp.const(len(opts)), invalid_symbol)
    comp.clear(inp)
    comp.get_int("-1", inp)
    comp.clear(skpval)
    comp.jumptbl(ch,opts)

    comp.set_tag(add)
    comp.add(inp, acc)
    comp.jump(tbl)

    comp.set_tag(sub)
    comp.sub(inp,acc)
    comp.jump(tbl)

    comp.set_tag(mult)
    comp.rev_mult(inp, acc)
    comp.jump(tbl)

    comp.set_tag(div)
    comp.eq(acc, "Z", tbl)
    comp.div(inp, acc)
    comp.jump(tbl)

    comp.set_tag(mod)
    comp.mod(inp, acc)
    comp.jump(tbl)

    comp.set_tag(invalid_symbol)
    comp.print_str("Invalid symbol. Valid operations are +,-,*,/,%.\n", "-1")
    comp.jump(tbl)

    compres = comp.compile()
    print(compres)
    asmed = asm(compres)
    fmtprint(asmed, compres)
    return asmed

def run_singlecore(asmed):
    tio = TextIO(255)
    h = Head(asmed, [tio])
    while True:
        h.advance()
        i = 0
        with tio.term.cbreak():
            h.advance()
            potinp = ""
            if h.ip < 0:
                potinp = tio.term.inkey(0.001)
                i = 10
            else:
                if i == 0:
                    potinp = tio.term.inkey(0.0001)
                    i = 1000
                i += -1
            if len(potinp) == 1:
                tio.keys.append(ord(potinp))

class IOHusk(IO):
    def __init__(self):
        self.inp = ""
        self.out = ""

    def set(self, x):
        self.out += chr(x)
    def get(self):
        if self.inp == "":
            return 0
        else:
            v = ord(self.inp[0])
            self.inp = self.inp[1:]
            return v
    def has_val(self) -> bool:
        return len(self.inp) != 0

def fmtout(inp:str, width):
    buf = [""]
    for c in inp:
        if c == "\n":
            buf.append("")
            continue
        if len(buf[-1]) == width:
            buf.append("")
        buf[-1] += c
    return buf


def run_dualcore(asmed1, asmed2, boost):
    term = blessed.Terminal()
    print(term.home + term.clear)
    with term.cbreak():
        for i in range(0,term.height):
            print(term.move_xy(term.width//2,i)+"|", end="",flush=True)
        sio = IOHusk()
        fio = IOHusk()
        p = pair()
        first = Head(asmed1,[fio,p[0]])
        second = Head(asmed2, [p[1],sio])
        fbuf = ""
        sbuf = ""
        l = True
        while True:
            for _ in range(boost):
                first.advance()
                second.advance()
            fout = fmtout(fio.out, (term.width//2 - 1))
            print(term.move_xy(0,0),end="",flush=True)
            for line in fout[max(len(fout) - (term.height -2), 0):]:
                print(line,flush=True)
            sout = fmtout(sio.out, (term.width//2 - 1))
            print(term.move_xy(term.width//2 + 1,0),end="",flush=True)
            for line in sout[max(len(fout) - (term.height -2), 0):]:
                print(line,flush=True)
                print(term.move_x(term.width//2 + 1), end="", flush=True)

            curpos = 0
            if l:
                curpos = min(len(fbuf),(term.width//2 -1))
            else:
                curpos = (term.width//2) + 1+ min(len(sbuf),(term.width//2 -1))
            print(term.move_xy(0,term.height), 
                fbuf[max(len(fbuf) - (term.width//2), 0):], 
                " " * max(0,((term.width//2 -1) - len(fbuf))),
                term.move_xy(term.width//2 + 1,term.height), 
                sbuf[max(len(sbuf) - (term.width//2 - 1), 0):],
                " " * max(0,((term.width//2 -1) - len(sbuf))),
                term.move_xy(curpos,term.height), sep="",end="",flush=True)
            key = term.inkey(0.01)
            if key == "":
                continue
            if key.is_sequence:
                match key.name:
                    case "KEY_BACKSPACE":
                        if l:
                            fbuf = fbuf[:-1]
                        else:
                            sbuf = sbuf [:-1]
                    case "KEY_TAB":
                        l = not l
                    case "KEY_ENTER":
                        if l:
                            fio.inp += (fbuf+"\n")
                            fbuf = ""
                        else:
                            sio.inp += (sbuf+"\n")
                            sbuf = ""
            else:
                if l:
                    fbuf += str(key)
                else:
                    sbuf += str(key)


if __name__ == "__main__":
    c1 = asm("""#skip reading on first start, as IO may not have value
Z:Z Z j:?+1
j j ?+1 #set j to zero

#add tgtp to j
tgtp h0 ?+1
h0 j -1

tgt:-1 -2 -1 #Read from Processor 1 and write to IO.

tgtp:tgt""")
    c2 = asm("""#skip reading on first start, as IO may not have value
Z:Z Z j:?+1
j j ?+1 #set j to zero

#add tgtp to j
tgtp h0 ?+1
h0 j -1

tgt:-1 -2 -1 #Read from Processor 1 and write to IO.

tgtp:tgt""")
    run_dualcore(c1, c2, 32)
    #p = pair()
    #fio = IOHusk()
    #sio = IOHusk()
    #first = Head(c1, [fio, p[0]])
    #second = Head(c2, [p[1],sio])
    #while True:
    #    first.advance()
    #    second.advance
    #    print(fio.out)
    #    print(sio.out)