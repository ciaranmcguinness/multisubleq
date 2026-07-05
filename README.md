# MulitSubleq

Subleq... but in parallel!

## What is Subleq?

Subleq is an esoteric assembely language featuring a single opcode, the epononymous subleq, or subtract and jump if less than or equal to zero. The instruction takes 3 arguments, a, b, and c. It then reads from the memory addresses specified by a and b, subtracts a* from b*, stores that value into the address specifified by b, and increments the instruction pointer either by 3 or c, depending on if the resulting value is less than or equal to zero. 

This does not specify how IO works, so conventionally, it is mapped to -1. When a = -1, it reads from IO. When b = -1, it writes A* to IO. Additionally, IP being less than zero is treated as halting.

## What is MultiSubleq?

MultiSubleq is a superset of regular subleq. Its 2 main diferentiators are: 
1. Allowing for multiple IO channels, by assigning each a magic number, equal to "((i - 1) * -1)" where i equals the channel's index in the list of channels.
2. Introducing a system by which the processor can halt until a value is available from an IO channel, by jumping to that channel's magic number.