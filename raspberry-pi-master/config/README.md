# Configuring the system image

*ROVERS* system image is a modified version of *Rasbpbian Stretch with desktop 4.14*. Each modification is further described to allow replication and re-configuration of the system.

## Modifications

Here is a full list of changes introduced to the system. Naturally, before installing any of them you should `update` and `upgrade` your system via `apt-get`.

1. `VNC`, `SSH` activation
2. `Python3.6` installation
3. *Python* libraries installation via `pip`
4. Server start on boot
5. `OpenCV` installation (pending)

### 1. VNC-SSH-activation

- Launch Raspberry Pi Configuration from the *Preferences* menu
- Navigate to the *Interfaces* tab
- Enable *SSH* and *VNC*

### 2. Python3.6 installation

Run the following block of commands:

```commandline
sudo apt-get install build-essential checkinstall
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
sudo -i
cd /usr/src
wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tgz
tar xzf Python-3.6.4.tgz
cd Python-3.6.4
bash configure
make altinstall
```

### 3. Python libraries installation via pip

Run the following block of commands:

```commandline
sudo python3.6 -m pip install --upgrade pip
sudo python3.6 -m pip install pyserial
sudo python3.6 -m pip install dill
```

### 4. Server start on boot

1. Run the following command:

```commandline
sudo nano /etc/rc.local
```

2. Add the following line to the file (before the default script which can print IP):

```
sudo python3.6 /home/pi/Desktop/ROV/main.py 2> /home/pi/Desktop/ROV/error_log &
```

Example file content:

```
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

# Run the server
sudo python3.6 /home/pi/Desktop/ROV/main.py & 2> /home/pi/Desktop/ROV/error_log

# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
printf "My IP address is %s\n" "$_IP"
fi

exit 0
```

3. Add the following `startup.service` file into `/etc/systemd/system`:

```
[Unit]
Description=Running /etc/rc.local
ConditionPathExists=/etc/rc.local

[Service]
Type=forking
ExecStart=/bin/sh /etc/rc.local start
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

4. Run the following block of commands:

```commandline
sudo systemctl daemon-reload
sudo systemctl enable startup.service
```

Sources:

1. https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/

2. https://www.raspberrypi.org/documentation/linux/usage/systemd.md

### 5. OpenCV installation

Installation of OpenCV is done by doing the following. Running of commands is done in a terminal.

1. Step #1

Run the following command

```commandline
sudo raspi-config
```

Select "Advanced Options"

Select "Expand Filesystem"

Select "Finish"

Reboot Pi

```commandline
sudo reboot
```
2. Step #2

If the Pi is using an 8GB microSD card then once the pi is rebooted run the following commands. If the microSD is larger than 8GB then skip this step.

```commandline
sudo apt-get purge wolfram-engine
$ sudo apt-get purge libreoffice*
$ sudo apt-get clean
$ sudo apt-get autoremove
```

3. Step #3

Update system and install dependencies by running the following commands

```commandline
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install build-essential cmake unzip pkg-config
sudo apt-get install libjpeg-dev libpng-dev libtiff-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get install libxvidcore-dev libx264-dev
sudo apt-get install libgtk-3-dev
sudo apt-get install libcanberra-gtk*
sudo apt-get install libatlas-base-dev gfortran
sudo apt-get install python3-dev
```

4. Step #4

Download OpenCV to the pi.

Run the following commands.

While there are newer releases than 4.0.1 this is the only version which has been tested so far.

```commandline
cd ~
wget -O opencv.zip https://github.com/opencv/opencv/archive/4.0.1.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.0.1.zip
unzip opencv.zip
unzip opencv_contrib.zip
mv opencv-4.0.1 opencv
mv opencv_contrib-4.0.1 opencv_contrib
```

5. Step #5

Install numpy using the following command:
```commandline
sudo python3.6 -m pip install numpy
```
6. Step #6

Move into the opencv directory and create a `build` subdirectory 

```commandline
cd ~/opencv
mkdir build
cd build
```

run cmake to configure the build.

```commandline
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
    -D ENABLE_NEON=ON \
    -D ENABLE_VFPV3=ON \
    -D BUILD_TESTS=OFF \
    -D OPENCV_ENABLE_NONFREE=ON \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D BUILD_EXAMPLES=OFF ..
```

7. Step #7

Increase the swap space on the Pi.

Open the swapfile

```commandline
sudo nano /etc/dphys-swapfile
```

Edit the `CONF_SWAPSIZE` variable from the default 100MB to 2048MB

```
Install OpenCV 4 on your Raspberry PiShell
# set size to absolute value, leaving empty (default) then uses computed value
#   you most likely don't want this, unless you have an special disk situation
# CONF_SWAPSIZE=100
CONF_SWAPSIZE=2048
```
Save and exit the file.

Restart the swap service

```commandline
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
```

8. Step #8

compile OpenCV
```commandline
make -j3
```
This will only use 3 cores instead of all of the 4 cores possible. This is done because using all 4 cores is likely to cause the pi to freeze while compiling while using 3 leaves a single core for other threads to run on. Allowing for the monitoring of the compilation much more easily.

This does increase the amount of time the compilation could take (it can take hours)

9. Step #9

Install OpenCV

```commandline
sudo make install
sudo ldconfig
```

10. Step #10

Reduce swap size back to 100MB.

Open the swapfile

```commandline
sudo nano /etc/dphys-swapfile
```

Edit the `CONF_SWAPSIZE` variable from 2048MB back to the default 100MB

```
Install OpenCV 4 on your Raspberry PiShell
# set size to absolute value, leaving empty (default) then uses computed value
#   you most likely don't want this, unless you have an special disk situation
CONF_SWAPSIZE=100
```

Save and exit the file.

Restart the swap service

```commandline
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
```

11. Step #11

Link the install to the python 3.6 installation.

```commandline
cd /usr/local/lib/python3.6/site-packages/
ln -s /usr/local/python/cv2/python-3.5/cv2.cpython-35m-arm-linux-gnueabihf.so cv2.so
```

12. Step #12

Test the openCV install.

```commandline
python
```

```python
>>> import cv2
>>> cv2.__version__
'4.0.1'
>>> exit()
```


Sources:

1. https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/
    Minor changes have been made to both the format and content of the information found here. 
