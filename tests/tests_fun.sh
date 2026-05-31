##
## EPITECH PROJECT, 2024
## Trade
## File description:
## tests_fun
##

#!/bin/bash

python3 trade < exemple > tests/find/hi
cd tests/find/

if grep -r "pass"
then
    echo "[PASS]: test no actions"
else
    echo "[FAIL]: test no actions"
fi

if grep -r "buy USDT_BTC 0.011"
then
    echo "[PASS]: test buy"
else
    echo "[FAIL]: test buy"
fi

if grep -r "sell USDT_BTC 0.010978"
then
    echo "[PASS]: test sell"
else
    echo "[FAIL]: test sell"
fi

cd ../../