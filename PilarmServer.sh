#!/bin/sh

COMMAND="python3 /home/pi/Pilarm/PilarmServer.py"
LOGFILE="/home/pi/Pilarm/PilarmServerRestart.log"

#exec 2> /home/pi/debug.log  # send stderr to a log file
#exec 1>&2                   # send stdout to the same log file
#set -x                      # tell sh to display commands before execution

writelog() {
  now=`date +"%m-%d-%y %H:%M:%S"`
  echo "$now $*" >> $LOGFILE
}

writelog "Starting"
while true ; do
  $COMMAND
  writelog "Exited with status $?"
  writelog "Restarting"
done
