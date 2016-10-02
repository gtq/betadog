#!/bin/sh
PYTHONPROG='phedgemarket.py'
 
if ps ax | grep -v grep | pgrep -f $PYTHONPROG > /dev/null
then
    echo "$PYTHONPROG is still running, killing previous process"
    pkill -9 -f $PYTHONPROG
else
    echo "$PYTHONPROG is not running, starting process"
fi
/usr/bin/python $PYTHONPROG
