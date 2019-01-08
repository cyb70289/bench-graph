#!/bin/bash

tryrun() {
    echo '$' $@
    $@
    local err=$?
    [ "${err}" -ne "0" ] && { echo ERR; exit ${err}; }
}

bold=$(tput bold)
normal=$(tput sgr0)

echo ======================================================================
echo Copy test file to test nodes
echo ======================================================================
testfile=$1
[ -z "${testfile}" ] && { echo "test file not provided"; exit 1; }
[ -f "${testfile}" ] || { echo "test file not found: $1"; exit 1; }

while read host; do
    tryrun ssh -n ${host} "mkdir -p /tmp/isa-l-test/"
    tryrun scp -r ${testfile} ${host}:/tmp/isa-l-test/
done < test-hosts

echo ======================================================================
echo Run test on test nodes
echo ======================================================================
shift 1
testcmd=$@
[ -z "${testcmd}" ] && testcmd="./$(basename ${testfile})"

while read host; do
    echo ---------------------------------------------------------------------
    echo "Test on ${bold}${host}${normal}: cd /tmp/isa-l-test && ${testcmd}"
    ssh -n ${host} "echo -n 'page size: '; getconf PAGESIZE;                \
                    echo -n 'load average: '; cut /proc/loadavg -f1 -d' ';  \
                    cd /tmp/isa-l-test && ${testcmd}"
    [ $? = 0 ] || { echo ERR; exit 1; }
done < test-hosts
