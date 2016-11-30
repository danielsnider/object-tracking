# installing ubuntu on rasbpi
# https://wiki.ubuntu.com/ARM/RaspberryPi

# overclocking ubuntu / raspberry pi
# https://www.youtube.com/watch?v=UGSQ7nzVCs4

# note you can build your own ubuntu raspberry image based on this:
# http://www.finnie.org/software/raspberrypi/rpi2-build-image.sh


# attach SD card to laptop
sudo bmaptool copy --bmap 2015-03-02-ubuntu-trusty.bmap 2015-03-02-ubuntu-trusty.img /dev/sdf

# boot in RPI and boot

# edit /etc/modprobe.d/modprobe.conf and add:
# disable autoload of ipv6
alias net-pf-10 off

# overclock
cat << EOF >> /boot/config.txt
# overclock to 1ghz
arm_freq=1000
core_freq=500
sdram_freq=500
over_voltage=2
gpu_mem=512
EOF

fdisk /dev/mmcblk0
# Delete the second partition (d, 2), then re-create it using the defaults (n, p, 2, enter, enter), then write and exit (w). Reboot the system, then:

resize2fs /dev/mmcblk0p2


apt-get update
apt-get upgrade
apt-get install openssh-server nfs-common
# apt-get remove libraspberrypi-bin libraspberrypi-dev


#all 
sudo apt-get install build-essential cmake pkg-config unzip vim libjpeg8-dev libtiff4-dev libjasper-dev libpng12-dev libgtk2.0-dev libatlas-base-dev gfortran python-pip python2.7-dev avahi-daemon avahi-utils

# Install the required developer tools and packages:
sudo apt-get install build-essential cmake pkg-config unzip vim

# Install the necessary image I/O packages. These packages allow you to load various image file formats such as JPEG, PNG, TIFF, etc.
sudo apt-get install libjpeg8-dev libtiff4-dev libjasper-dev

# skipped because I don't need opencv's high gui
sudo apt-get install libgtk2.0-dev
# i did this instead to fix "HIGHGUI ERROR: V4L/V4L2: VIDIOC_S_CROP" then ran cmake step again
# sudo apt-get install v4l2ucp v4l-utils libv4l-dev
# wisdom: "P.S. Note to the developers: you could add a sanity check for libv4l-dev if compiling with V4L."
# compile options: "I cross-compiled OpenCV 2.4.4 and built it WITH_GTK=ON, WITH_UNICAP=ON, WITH_V4L=ON as needed for camera and GUI support."
# http://stackoverflow.com/questions/16287488/runtime-opencv-highgui-error-highgui-error-v4l-v4l2-vidioc-s-crop-opencv-c

# Install libraries that are used to optimize various operations within OpenCV:
apt-get install libatlas-base-dev gfortran

# Install pip
apt-get install python-pip

# Install  virtualenv  and virtualenvwrapper
pip install virtualenv virtualenvwrapper

# Then, update your ~/.profile  file to include the following lines:
su ubuntu
cat << EOF >> ~/.profile

# virtualenv and virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
EOF

source ~/.profile

# Create your computer vision virtual environment:
mkvirtualenv cv

sudo apt-get install python2.7-dev

# # for opencv version 2.4.8 
# # this is easier to automate!
# sudo apt-get install python-numpy
# sudo apt-get install python-scipy
# sudo apt-get install python-imaging
# sudo apt-get install libopencv-dev
# sudo apt-get install python-opencv

pip install numpy


#######
https://wiki.ubuntu.com/ARM/RaspberryPi#Usage

An accelerated x.org video driver is available (fbturbo), though this is limited to hardware accelerated window moving/scrolling on the Raspberry Pi. To install:

$ sudo apt-get install xserver-xorg-video-fbturbo
Then add this to /etc/X11/xorg.conf (create if it doesnt already exist):

Section "Device"
    Identifier "Raspberry Pi FBDEV"
    Driver "fbturbo"
    Option "fbdev" "/dev/fb0"
    Option "SwapbuffersWait" "true"
EndSection
As with Raspbian, VideoCore packages are available:

$ sudo apt-get install libraspberrypi-bin libraspberrypi-dev
However, since these packages are compiled from source during build, the files are installed in their "proper" locations in /usr. Some third-party scripts may expect e.g. /opt/vc/bin/vcgencmd; if so, this hack should do it:

$ sudo ln -s /usr /opt/vc
(Raspbian packages use precompiled repositories during build, which install in /opt/vc.) vcdbg and edidparser are not part of the open source package and must be installed separately:

$ sudo apt-get install libraspberrypi-bin-nonfree
Serial console / login
##############33

# Note: we are going to use Python 2.7. OpenCV 2.4.X does not yet support Python 3 and OpenCV 3.0 is still in beta. It’s also unclear when the Python bindings for OpenCV 3.0 will be complete so I advise to stick with OpenCV 2.4.X for the time being.
# Download opencv
wget -O opencv-2.4.10.zip http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.10/opencv-2.4.10.zip/download
unzip opencv-2.4.10.zip
cd opencv-2.4.10

# setup the build
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON  -D BUILD_EXAMPLES=ON ..

# compile
make

# install 
sudo make install
sudo ldconfig

# OpenCV should now be installed in  /usr/local/lib/python2.7/site-packages
# But in order to utilize OpenCV within our cv  virtual environment, we first need to sym-link OpenCV into our site-packages  directory:
cd ~/.virtualenvs/cv/lib/python2.7/site-packages/
ln -s /usr/local/lib/python2.7/site-packages/cv2.so cv2.so
ln -s /usr/local/lib/python2.7/site-packages/cv.py cv.py

# test opencv
workon cv
python
>>> import cv2
>>> cv2.__version__
'2.4.10'


$ which pip
/home/ubuntu/.virtualenvs/cv/bin/pip

pip install tornado
# pip install numpy



ssh ubuntu@192.168.0.105

#NFS mount code from server (great way to apply updates and quick changes!!)
sudo mount 192.168.0.104:/home/dan/pt /home/ubuntu/pt
sudo mount 192.168.0.101:/home/dan/pt/player-tracking-combined /home/ubuntu/pt

# global
sudo su
cat << EOF >> /usr/lib/python2.7/sitecustomize.py
import sys
sys.path.append('/home/ubuntu/pt/pt-pt')
sys.path.append('/home/ubuntu/pt/pt-client')
sys.path.append('/home/ubuntu/pt/pt-cookbook')
sys.path.append('/home/ubuntu/pt/pt-cv')
sys.path.append('/home/ubuntu/pt/pt-freight')
sys.path.append('/home/ubuntu/pt/pt-server')
sys.path.append('/home/ubuntu/pt/pt-website')
sys.path.append('/home/ubuntu/pt/pt-zklib')
sys.path.append('/usr/local/lib/python2.7/site-packages')
EOF

# virtualenv
ln -s /home/ubuntu/pt/pt /home/ubuntu/.virtualenvs/cv/lib/python2.7/site-packages/
ln -s /home/ubuntu/pt/pt-client /home/ubuntu/.virtualenvs/cv/lib/python2.7/site-packages/
ln -s /home/ubuntu/pt/pt-cookbook /home/ubuntu/.virtualenvs/cv/lib/python2.7/site-packages/
ln -s /home/ubuntu/pt/pt-cvutils /home/ubuntu/.virtualenvs/cv/lib/python2.7/site-packages/
ln -s /home/ubuntu/pt/pt-freight /home/ubuntu/.virtualenvs/cv/lib/python2.7/site-packages/
ln -s /home/ubuntu/pt/pt-server /home/ubuntu/.virtualenvs/cv/lib/python2.7/site-packages/
ln -s /home/ubuntu/pt/pt-website /home/ubuntu/.virtualenvs/cv/lib/python2.7/site-packages/
ln -s /home/ubuntu/pt/pt-zklib /home/ubuntu/.virtualenvs/cv/lib/python2.7/site-packages/



which /usr/lib/arm-linux-gnueabihf/libv4l/v4l2convert.so python
which /usr/lib/arm-linux-gnueabihf/libv4lconvert.so.0.0.0 python
which /usr/lib/arm-linux-gnueabihf/libv4lconvert.so python
which /usr/lib/arm-linux-gnueabihf/gstreamer-1.0/libgstvideoconvert.so python
which /usr/lib/arm-linux-gnueabihf/libv4lconvert.so.0 python

LD_PRELOAD=/usr/lib/i386-linux-gnu/libv4l/v4l2convert.so python filename.py
LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libv4l/v4l2convert.so python ./ptclient/ptclient.py
LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libv4lconvert.so.0.0.0 python ./ptclient/ptclient.py
LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libv4lconvert.so python ./ptclient/ptclient.py
LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/gstreamer-1.0/libgstvideoconvert.so python ./ptclient/ptclient.py
LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libv4lconvert.so.0 python ./ptclient/ptclient.py



# ERROR
[ 17%] Building CXX object modules/ts/CMakeFiles/opencv_ts.dir/src/ts_func.cpp.o
/home/ubuntu/cv/opencv-2.4.10/modules/ts/src/ts_func.cpp: In function ‘cv::Scalar cvtest::mean(const cv::Mat&, const cv::Mat&)’:
/home/ubuntu/cv/opencv-2.4.10/modules/ts/src/ts_func.cpp:2634:37: internal compiler error: in template_decl_level, at cp/pt.c:16162
     return sum * (1./std::max(nz, 1));
                                     ^
Please submit a full bug report,
with preprocessed source if appropriate.
See <file:///usr/share/doc/gcc-4.8/README.Bugs> for instructions.
Preprocessed source stored into /tmp/ccTssIlf.out file, please attach this to your bugreport.
make[2]: *** [modules/ts/CMakeFiles/opencv_ts.dir/src/ts_func.cpp.o] Error 1
make[1]: *** [modules/ts/CMakeFiles/opencv_ts.dir/all] Error 2
*** Error in `make`: malloc(): smallbin double linked list corrupted: 0x015b18e0 ***
Aborted


# ERROR
[ 18%] Building CXX object modules/core/CMakeFiles/opencv_perf_core.dir/perf/perf_math.cpp.o
/home/ubuntu/cv/opencv-2.4.10/modules/core/perf/perf_math.cpp: In member function ‘virtual void MaxDim_MaxPoints_kmeans::PerfTestBody()’:
/home/ubuntu/cv/opencv-2.4.10/modules/core/perf/perf_math.cpp:59:54: internal compiler error: Segmentation fault
     Mat clusterPointsNumber = Mat::zeros(1, K, CV_32S);
                                                      ^
Please submit a full bug report,
with preprocessed source if appropriate.
See <file:///usr/share/doc/gcc-4.8/README.Bugs> for instructions.
The bug is not reproducible, so it is likely a hardware or OS problem.
make[2]: *** [modules/core/CMakeFiles/opencv_perf_core.dir/perf/perf_math.cpp.o] Error 1
make[1]: *** [modules/core/CMakeFiles/opencv_perf_core.dir/all] Error 2
make: *** [all] Error 2


sudo apt-get install triggerhappy

wget http://archive.raspberrypi.org/debian/pool/main/r/raspi-config/raspi-config_20150131-1_all.deb
sudo dpkg -i raspi-config_20150131-1_all.deb
# or

# sudo echo "deb http://archive.raspbian.org/raspbian wheezy main contrib non-free
# deb-src http://archive.raspbian.org/raspbian wheezy main contrib non-free" >> /etc/apt/sources.list

# wget http://archive.raspbian.org/raspbian.public.key -O - | sudo apt-key add -

# sudo apt-get update
# sudo apt-get install raspi-config
sudo raspi-config
# enable camera 

pip install picamera
# or 
# apt-get install python-picamera

# capture video
# http://www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/


# GPU Usage
sudo vcdbg hist
gnuplot task.gpt
# or
sudo vcdbg reloc






















# Raspbery Pi 1
# Download raspbian image
# https://www.raspberrypi.org/downloads/

# Install SD card guide
# https://www.raspberrypi.org/documentation/installation/installing-images/linux.md
dcfldd bs=4M if=/home/dan/Downloads/2015-02-16-raspbian-wheezy.img  of=/dev/sdb


# install OpenCV
# http://robertcastle.com/2014/02/installing-opencv-on-a-raspberry-pi/

# Default login:pi / raspberry
