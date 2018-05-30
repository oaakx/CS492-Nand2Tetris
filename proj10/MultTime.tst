// Measure running time of Mult.asm

load Mult.asm,
output-file MultTime.out,
output-list RAM[0]%D2.6.2 RAM[1]%D2.6.2 RAM[2]%D2.6.2 time%S1.5.1;

set RAM[0] 2,
set RAM[1] 3,
set RAM[2] -1;
while RAM[2] <> 6 {
  ticktock;
}
output;

set PC 0,
set RAM[0] 17,
set RAM[1] 123,
set RAM[2] -1;
while RAM[2] <> 2091 {
  ticktock;
}
output;

set PC 0,
set RAM[0] 197,
set RAM[1] 137,
set RAM[2] -1;
while RAM[2] <> 26989 {
  ticktock;
}
output;

set PC 0,
set RAM[0] 13,
set RAM[1] 2333,
set RAM[2] -1;
while RAM[2] <> 30329 {
  ticktock;
}
output;

set PC 0,
set RAM[0] 2333,
set RAM[1] 13,
set RAM[2] -1;
while RAM[2] <> 30329 {
  ticktock;
}
output;

set PC 0,
set RAM[0] 8888,
set RAM[1] 3,
set RAM[2] -1;
while RAM[2] <> 26664 {
  ticktock;
}
output;

set PC 0,
set RAM[0] 3,
set RAM[1] 8888,
set RAM[2] -1;
while RAM[2] <> 26664 {
  ticktock;
}
output;
