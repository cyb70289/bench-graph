# https://github.com/cyb70289/mytests/blob/master/cpp/mode-range.cc

echo "count,range,speedup" > mode-range.csv

RANGE="2048 4096 8192 16384 32768 65536 131072"
COUNT="200 500 1000 2000 3000 4500 7000 10000 30000 100000 1000000 10000000"

for range in $RANGE; do
    for count in $COUNT; do
        ./mode-range $range $count;
    done;
done 2>> mode-range.csv
