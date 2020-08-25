BEGIN {print "Mode,Threads,Bandwidth,Latency"}
/TEST GET/ {mode="get"}
/TEST PUT/ {mode="put"}
/threads =/ {thread=$3}
/Speed/ {speed=$2}
/Latency mean/ { printf "%s,%s,%s,%s\n",mode,thread,speed,$3 }
