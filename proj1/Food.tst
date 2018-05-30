load Food.hdl,
output-file Food.out,
output-list potatoes%B3.1.3 noodles%B3.1.3 bread%B3.1.3 cond1%B3.1.3 cond2%B3.1.3 cond3%B3.1.3 ;
set potatoes 0,
set noodles 0,
set bread 0,
eval,
output;

set potatoes 1,
set noodles 0,
set bread 0,
eval,
output;

set potatoes 0,
set noodles 1,
set bread 0,
eval,
output;

set potatoes 1,
set noodles 1,
set bread 0,
eval,
output;

set potatoes 0,
set noodles 0,
set bread 1,
eval,
output;

set potatoes 1,
set noodles 0,
set bread 1,
eval,
output;

set potatoes 0,
set noodles 1,
set bread 1,
eval,
output;

set potatoes 1,
set noodles 1,
set bread 1,
eval,
output;

