# MulitSubleq

Subleq... but in parallel!

[Try on the web!](https://cmcg.pyscriptapps.com/jolly-union/)

## What is Subleq?

Subleq is an esoteric assembly language featuring a single opcode, the epononymous subleq, or subtract and jump if less than or equal to zero. The instruction takes 3 arguments, a, b, and c. It then reads from the memory addresses specified by a and b, subtracts a* from b*, stores that value into the address specifified by b, and increments the instruction pointer either by 3 or c, depending on if the resulting value is less than or equal to zero. 

This does not specify how IO works, so conventionally, it is mapped to -1. When a = -1, it reads from IO. When b = -1, it writes A* to IO. Additionally, IP being less than zero is treated as halting.

## What is MultiSubleq?

MultiSubleq is a superset of regular subleq. Its 2 main diferentiators are: 
1. Allowing for multiple IO channels, by assigning each a magic number, equal to "((i - 1) * -1)" where i equals the channel's index in the list of channels.
2. Introducing a system by which the processor can halt until a value is available from an IO channel, by jumping to that channel's magic number.

## Usage

The interpreter is available in 2 formats:
1. [The website](https://cmcg.pyscriptapps.com/jolly-union/), which is easier to use and doesn't require cloning this repo
2. The CLI, which requires you to clone this repo and requires editing the code for more advanced functions, but probably runs faster, is easier to debug your programs in, includes the `Compiler` class from multi.py which makes writing programs way easier, and includes some more complex demos, such as the 5 function (add, subtract, multiply, interger divide, and modulus) calcualtor.

## How does one "MultiSubleq"?

If it's at all possible, I would advise using the compiler-thing I have in multi.py, its way better than writing by hand. But, if you truly want to write assembly, since MultiSubleq is based on subleq, [the esolangs page on subleq](https://esolangs.org/wiki/Subleq) is able to get you up to speed. So the following is mostly stuff to help someone who already understands subleq.


* Skip running on inital start, so that a processor can run only when invoked by user input or another processor.
```
Z:Z Z j:?+1
j j ?+2 tgt:YOUR_ENTRY_POINT_HERE
tgtp h0 ?+1
h0 j -1
```
* Forward input from IO to processor 2.
```
-1 -2 ?+1
```

## AI
I had claude write the HTML for the demo, because CSS is pain and misery.