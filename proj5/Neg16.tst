// Test script for Neg16.hdl

load Neg16.hdl,
output-file Neg16.out,
compare-to Neg16.cmp,
output-list a%B1.16.1 negate%D2.1.2 out%B1.16.1;

set a %B0000000000000000,
set negate 0,
eval,
output;

set negate 1,
eval,
output;

set a %B1001100001110110,
set negate 0,
eval,
output;

set negate 1,
eval,
output;

set a %B1010101010101010,
set negate 0,
eval,
output;

set negate 1,
eval,
output;
