// Test script for Zero16.hdl

load Zero16.hdl,
output-file Zero16.out,
compare-to Zero16.cmp,
output-list a%B1.16.1 zero%D2.1.2 out%B1.16.1;

set a %B0000000000000000,
set zero 0,
eval,
output;

set zero 1,
eval,
output;

set a %B1001100001110110,
set zero 0,
eval,
output;

set zero 1,
eval,
output;

set a %B1010101010101010,
set zero 0,
eval,
output;

set zero 1,
eval,
output;
