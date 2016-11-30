#!/bin/bash

if [ -z "$1" ]
  then
    echo "No argument supplied"
    exit 1

fi

IP_ARG=$1
SIZE=${#IP_ARG}

if [ "$SIZE" -gt "3" ]; then
    SEARCH_NET=$IP_ARG
else
    SEARCH_NET="192.168.$IP_ARG.0/24"
fi

PI_IPS=$(sudo nmap -sP $SEARCH_NET | awk '/^Nmap/{ip=$NF}/B8:27:EB/{print ip}')



for IP in $PI_IPS; do
    echo "Connecting to $IP..."
    ssh ubuntu@$IP
done
