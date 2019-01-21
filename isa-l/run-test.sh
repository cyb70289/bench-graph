#!/bin/bash

# Copy and run test on hosts
# - test hosts defined in file test-hosts, password-less ssh must be setup
# - scp test binary(or directory) to host:/tmp/isa-l-test/
# - ssh and enter host:/tmp/isa-l-test/, run test command
# - append console outputs to _test-file-name_.log
#
# Examples
# $ ./run_test.sh ../isa-l/xor_gen_perf
# $ ./run_test.sh /home/linux/mytests mytests/start

tryrun() {
    echo '$' $@
    $@
    local err=$?
    [ "${err}" -ne "0" ] && { echo ERR; exit ${err}; }
}

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
    # strip username: ubuntu@wls-arm-qc01 ==> wls-arm-qc01
    HOST=$(sed 's/^.*@//' <<< "${host}")
    echo ---------------------------------------------------------------------
    echo "Test on ${HOST}: cd /tmp/isa-l-test && ${testcmd}"
    ssh -n ${host} "echo -n 'page size: '; getconf PAGESIZE;                \
                    echo -n 'load average: '; cut /proc/loadavg -f1 -d' ';  \
                    cd /tmp/isa-l-test && ${testcmd}"
    [ $? = 0 ] || { echo ERR; exit 1; }
done < test-hosts | tee -a _${testfile}_.log
