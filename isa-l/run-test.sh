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
    # skip commented hosts
    [[ ${host} =~ ^[\ \t]*# ]] && continue
    tryrun ssh -n ${host} "mkdir -p /tmp/isa-l-test/"
    tryrun scp -r ${testfile} ${host}:/tmp/isa-l-test/
done < test-hosts

echo ======================================================================
echo Run test on test nodes
echo ======================================================================
shift 1
testcmd=$@
testfile="$(basename ${testfile})"
(echo ======================================================================;
 echo $(date +"%Y-%m-%d %T");) >> _${testfile}_.log
[ -z "${testcmd}" ] && testcmd=./${testfile}

while read host; do
    # skip commented hosts
    [[ ${host} =~ ^[\ \t]*# ]] && continue
    # strip username: ubuntu@wls-arm-qc01 ==> wlls-arm-qc01
    HOST=$(sed 's/^.*@//' <<< "${host}")
    echo ---------------------------------------------------------------------
    echo "Test on ${bold}${HOST}${normal}: cd /tmp/isa-l-test && ${testcmd}"
    ssh -n ${host} "echo -n 'page size: '; getconf PAGESIZE;                \
                    echo -n 'load average: '; cut /proc/loadavg -f1 -d' ';  \
                    cd /tmp/isa-l-test && ${testcmd}"
    [ $? = 0 ] || { echo ERR; exit 1; }
done < test-hosts | tee -a _${testfile}_.log

# drop color code
sed -i _${testfile}_.log -e 's/\x1b\[[0-9]*m//g' -e 's/\x0f//g'
