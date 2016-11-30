#!/bin/bash
# Recommended log file: /opt/pt/log/save_mac.log

usage="Usage: $SELF [-l logfile]"

# Get command line arguments if any
while getopts ":l:" opt; do
  case $opt in
    l)
      # Rerun $0 with output redirected to log file
      LOGFILE=$OPTARG
      $0 >> $LOGFILE 2>&1
      exit $?
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      echo $usage
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      echo $usage
      exit 1
      ;;
  esac
done

if [ -z "$ID_FS_UUID" ]
then
    exit 2
fi

echo ""
echo "New kingston device detected!"
echo "Model: $ID_MODEL"

# Mount USB device
USB="/mnt/$ID_FS_UUID" # CA0D-84D0
mkdir $USB -p
mount -t $ID_FS_TYPE $DEVNAME $USB #/dev/sdb1

echo "Mounted $ID_MODEL from $DEVNAME to $USB"

# Create working directory
mkdir $USB/pt -p

# Find file with name that is the largest number
max=-1
for file in $(ls $USB/pt); do
    # check if file is number
    if [[ $file =~ ^-?[0-9]+$ ]]
    then
        # check if this number is bigger than our current max
        if (($file > $max))
        then
            max=$file
        fi
    fi
done

# Write mac address to a file named with a number one greater than any other
# file in the working directory on the USB device
filename=$((max + 1))
# TODO: check that ethernet device exists
MAC=$(cat /sys/class/net/eth0/address)
echo "$MAC" > $USB/pt/$filename
echo "Wrote MAC $MAC to file $USB/pt/$filename"

# Clean up
echo "Unmounting $ID_MODEL from $USB"
umount $USB
echo "Done."
