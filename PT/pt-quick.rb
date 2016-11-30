http://elinux.org/Rpi_Camera_Module

# attach SD card to laptop
sudo bmaptool copy --bmap 2015-03-02-ubuntu-trusty.bmap 2015-03-02-ubuntu-trusty.img /dev/sdb

# boot in RPI and boot
# username: ubuntu
# passwork: ubuntu
ip a s
sudo apt-get update
sudo apt-get install openssh-server
# ssh to pi

# edit /etc/modprobe.d/modprobe.conf and add:
# disable autoload of ipv6
alias net-pf-10 off

fdisk /dev/mmcblk0
# Delete the second partition (d, 2), then re-create it using the defaults (n, p, 2, enter, enter), then write and exit (w). Reboot the system, then:

resize2fs /dev/mmcblk0p2


sudo apt-get upgrade -y && sudo apt-get install -y build-essential cmake pkg-config unzip vim libjpeg8-dev libtiff4-dev libjasper-dev libpng12-dev libgtk2.0-dev libatlas-base-dev gfortran python-pip python2.7-dev python-numpy python-scipy python-imaging libopencv-dev python-opencv nfs-common python-picamera triggerhappy curl
 
python
import cv2
cv2.__version__
#'2.4.10'

pip install tornado

mkdir /home/ubuntu/pt

sudo mount 192.168.12.1:/home/dan/pt /home/ubuntu/pt

# <!-- wget http://archive.raspberrypi.org/debian/pool/main/r/raspi-config/raspi-config_20150131-1_all.deb
# sudo dpkg -i raspi-config_20150131-1_all.deb -->
# sudo echo "deb http://archive.raspbian.org/raspbian wheezy main contrib non-free
# deb-src http://archive.raspbian.org/raspbian wheezy main contrib non-free" >> /etc/apt/sources.list
# wget http://archive.raspbian.org/raspbian.public.key -O - | sudo apt-key add -
# sudo apt-get update
# sudo apt-get install raspi-config


im not sure this is needed
<!-- update firmware -->
curl -L --output rpi-update https://raw.githubusercontent.com/Hexxeh/rpi-update/master/rpi-update && sudo chmod +x rpi-update
rpi-update
<!-- reboot -->

sudo raspi-config
# enable camera 
# or
# this is better
echo "gpu_mem=256
start_x=1" >> /boot/config.txt


action
./client.sh

error
OSError: libmmal.so: cannot open shared object file: No such file or directory

fix
File Name: /etc/ld.so.conf.d/00-vmcs.conf
Contents:
/opt/vc/lib

Save the file. Run ldconfig to re-init your library paths and see if that fixes your issues.


action
./client.sh

error
* failed to open vchiq instance

fix
echo 'SUBSYSTEM=="vchiq",GROUP="video",MODE="0660"' > /etc/udev/rules.d/10-vchiq-permissions.rules
usermod -a -G video ubuntu


action
sudo raspi-config
# enable camera

error
there was an error running option 5 enable camera

fix
avoid this error
echo "gpu_mem=256
start_x=1" >> /boot/config.txt



iface eth0 inet static
address 192.168.12.12
netmask 255.255.255.0
gateway 192.168.12.1

sudo ifconfig eth0:0 192.168.12.12 netmask 255.255.255.0
sudo ifconfig eth0:0 192.168.12.1 netmask 255.255.255.0


sudo ln -s /usr/share/zoneinfo/Etc/Canada/Eastern /etc/localtime


ping 192.168.12.1

ping 192.168.0.120 -c 1
ping 192.168.0.114 -c 1
ping 192.168.12.12 -c 1


sudo ntpdate -s tick.utoronto.ca

#!/usr/bin/env python
from numpy import *
 
array_len = 10000000
 
a = zeros(array_len, dtype=float)
 
#import pickle
#f = open('test.pickle', 'wb')
#pickle.dump(a, f, pickle.HIGHEST_PROTOCOL)
#f.close()
 
import tables
h5file = tables.openFile('test.h5', mode='w', title="Test Array")
root = h5file.root
h5file.createArray(root, "test", a)
h5file.close()


sparkfun

70ft by 130ft

960x720
25 % jpeg