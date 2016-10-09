#!/bin/sh

COMMAND="python3 /home/pi/PilarmServer.py"
LOGFILE="/home/pi/PilarmServerRestart.log"

writelog() {
  now=`date`
  echo "$now $*" >> $LOGFILE
}

writelog "Starting"
while true ; do
  $COMMAND
  writelog "Exited with status $?"
  writelog "Restarting"
done
