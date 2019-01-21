#!/bin/bash

# Loop test predefined rounds
# - first arg is number of rounds
# - other args passed to run-test.sh
#
# Example
# $ ./loop-test.sh 10 ../xor_gen_perf

count=$1
shift 1

for i in $(seq ${count}); do
    echo "#################################################################"
    echo "# ROUND $i / ${count}"
    echo "#################################################################"
    ./run-test.sh $@
    sleep 5
done
