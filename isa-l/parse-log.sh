#!/bin/bash

# XXX: only supports raid parsing

# Parse log and append to csv file
# - Generate log file by run-tests.sh
# - Parse log file, extract information and append to csv file for analysis
#
# Example
# $ ./parse-log.sh _test-file-name_.log

[ $1 = "" ] && { echo log file needed; exit 1; }
[ -r $1 ] || { echo cannot read $1; exit 1; }

[ -r host2chip ] || { echo cannot read host2chip; exit 1; }

host_2_chip() {
    test_chip=""
    while read line; do
        local host_chip=($line)
        local host=${host_chip[0]}
        local chip=${host_chip[1]}
        if [[ $1 =~ ${host} ]]; then
            test_chip=${chip}
            return
        fi
    done < host2chip
}

error_exit() {
    echo ERR:${status}: ${line}
    exit 1
}

csvfile=$(sed 's/log$/csv/' <<< $1)

# header
if [ ! -f ${csvfile} ]; then
    echo time,case,host,chip,page-size,load-average,bandwidth > ${csvfile}
fi

# status: =, time, -, host, page, load, result
status="result"
while read line; do
    case ${status} in
    "result")
        if [[ ${line} =~ ^==== ]]; then
            status="="
        elif [[ ${line} =~ ^---- ]]; then
            status="-"
        else
            error_exit
        fi
        ;;
    "=")
        if [[ ${line} =~ .*[0-9][0-9]:[0-9][0-9]:[0-9][0-9].* ]]; then
            test_time=${line}
            status="time"
        else
            error_exit
        fi
        ;;
    "time")
        if [[ ${line} =~ ^---- ]]; then
            status="-"
        else
            error_exit
        fi
        ;;
    "-")
        if [[ ${line} =~ ^Test\ on ]]; then
            test_host=$(cut -d' ' -f3 <<< ${line} | tr -d ':')
            host_2_chip ${test_host}
            status="host"
        else
            error_exit
        fi
        ;;
    "host")
        if [[ ${line} =~ ^page\ size ]]; then
            test_page=$(cut -d' ' -f3 <<< ${line})
            status="page"
        else
            error_exit
        fi
        ;;
    "page")
        if [[ ${line} =~ ^load\ average ]]; then
            test_load=$(cut -d' ' -f3 <<< ${line})
            status="load"
        else
            error_exit
        fi
        ;;
    "load")
        if [[ ${line} =~ .*runtime.*MB/s$ ]]; then
            test_case=$(cut -d' ' -f1 <<< ${line} | tr -d ':')
            test_result=$(sed 's/.* \([0-9.]\+\) MB\/s/\1/' <<< ${line})
            echo -n ${test_time},${test_case},${test_host},${test_chip},
            echo ${test_page},${test_load},${test_result}
            status='result'
        fi
        ;;
    esac
done < $1 | tee -a ${csvfile}
