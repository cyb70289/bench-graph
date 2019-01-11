#!/bin/bash

count=$1
shift 1

for i in $(seq ${count}); do
    echo "#################################################################"
    echo "# ROUND $i / ${count}"
    echo "#################################################################"
    ./run-test.sh $@
    sleep 5
done
