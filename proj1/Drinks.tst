load Drinks.hdl,
output-file Drinks.out,
output-list wine%B3.1.3 water%B3.1.3 juice%B3.1.3 cond1%B3.1.3 cond2%B3.1.3 cond3%B3.1.3 ;
set wine 0,
set water 0,
set juice 0,
eval,
output;

set wine 1,
set water 0,
set juice 0,
eval,
output;

set wine 0,
set water 1,
set juice 0,
eval,
output;

set wine 1,
set water 1,
set juice 0,
eval,
output;

set wine 0,
set water 0,
set juice 1,
eval,
output;

set wine 1,
set water 0,
set juice 1,
eval,
output;

set wine 0,
set water 1,
set juice 1,
eval,
output;

set wine 1,
set water 1,
set juice 1,
eval,
output;

