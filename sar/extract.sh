#!/bin/bash -e

# $1: output file, $2: params to sar
function extract {
    outf=$1
    shift

    tmpf=$(mktemp)
    # drop first 2 lines and Average lines
    sar $@ -f scylla.sar | sed '1,2d' | grep -v '^Average' > "$tmpf"
    # drop repeated headers(blank line and next line)
    sed -i '/^$/,+1d' "$tmpf"
    # rename first column: "00:00:00" -> "logtime"
    sed -i '1s/^[0-9:]\{8\}/logtime /' "$tmpf"

    mv "$tmpf" "$outf"
    echo "OK: sar $@ -f scylla.sar > $outf"
}

# Usage:
#   ./extract.sh
#   ./extract.sh -s 12:00:00
export LC_TIME='C'
extract cpu.txt -P ALL $@ && sed -i '/all/d' cpu.txt
extract mem.txt -r $@
extract blk.txt -d -p $@
extract net.txt -n DEV $@
