#!/bin/bash
 
NetCard=wlan0                   # the netcard connected to the internet
PingTarget=192.168.1.1  # the ping target, router ip or website, etc: 192.168.1.1, www.bai>
LogFile=/home/pi/NetReconnector.log     # log file
LogAll=false                    # log msg no matter whether the net is connected, used to >

test -e $LogFile || touch $LogFile

time=$(date "+%Y/%m/%d %H:%M:%S")

ret=$(ping -c 1 -W 2 -I $NetCard $PingTarget | grep 'received' | cut -d ',' -f 2 | cut -d ' ' -f 2)

if [ "$ret" == "0" ]; then
    #sudo ifdown wlan0 && sudo ifup wlan0
    #sudo ifdown wlan0
    #sleep 5
    #sudo ifup --force wlan0
		sudo ip link set wlan0 down  | tee -a $LogFile
    sudo ip link set wlan0 up  | tee -a $LogFile
    echo "Try Reconnect: $?, $time" | tee -a $LogFile
else
    if [ "$LogAll" == "true" ]; then
        echo "Network is ok, ret = $ret, $time" | tee -a $LogFile
    fi
fi

exit 0