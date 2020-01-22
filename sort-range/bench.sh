# https://github.com/cyb70289/mytests/blob/master/cpp/sort-range.cc

echo "count,range,speedup" > sort-range.csv

RANGE="256 512 1024 2048 4096 8192 16384 32768 65536"
COUNT="200 300 500 700 1000 1500 2000 3000 4500 7000 10000 30000 100000 1000000"

for range in $RANGE; do
    for count in $COUNT; do
        ./sort-range $range $count;
    done;
done 2>> sort-range.csv
