# PI SETUP OVERVIEW

The framework has been tested primarily pi 4B's running Ubuntu 22.04 due to its compatibility with ROS2 Humble. 
It will also run on Ubuntu 23 and the current Raspbian release, although less testing has been done in those environments. These setup notes are based on our experiences for a **Pi 4B using Ubuntu 22.04.03**. As hardware and OS releases change you will need to adapt the guidance -- particularily if using Ubuntu 23 or Raspbian.

1) Flash card with base Ubuntu Desktp image 22.04 using Raspberry pi imager with minimal desktop enviroment, or use server and add desktop.

2) Press ctrl-option x to set initial wifi network config prior to flashing. Confirm setup using keyboard, mouse, monitor as the Raspbian Imager often does not set the wifi network credentials when flashing Ubuntu 22.04.

3) While connected with a keyboard and monitor you may wish to configure additional wifi networks the robot/pi will use.  

4) You must configure **USB0** on the Pi as an ethernet interface with a **static IP of 192.168.186.3/24** to use ROS2

5) Note - if editing wifi config **from the terminal**, on Ubuntu 22 after the initial boot you have to do so via:
```
	sudo nano /etc/netplan/50-cloud-init.yaml
	sudo netplan apply
``` 
otherwise the config changes will not survive reboot. 
Once done:
```
	reload wlan
	sudo ifdown wlan0
	sudo ifup wlan0
```
Then test from your computer that changes have succeed using the command
	`ping -a yourpibothostname.local`

6) Add any additional python libraries needed. See the [detailed Pi - ubuntu setup guide](#detailed-pi-install-instructions) if needed. 

# Create 3 ROBOT SETUP
These instructions rely on the following ICreate guides
## ICREATE DOCS AND GUIDE:
- [ICreate Provisioning guide](https://iroboteducation.github.io/create3_docs/setup/provision/)
- [ICreate Robot setup guide](https://edu.irobot.com/create3-setup)

## QUICK SUMMARY OF ROBOT CONNECTION
1) CONNECT robot to your local network by entering setup mode and then accessing the robot in hotspot mode via web interface. 
	- Press buttons 1 and 3 on bot til it turns blue
	- Connect to robot hotspot then go to  http://192.168.10.1
	- On the connect and configuration pages set details for the wifi network you will use, along with settng the bluetooth / wifi hostnames and the ROS namespace. The namespace and bluetooth host name needs to match those set in the PIBOT environment. For example we used pibot1, pibot2, pibot3 etc
	- Save configuration and let the robot reboot.
2) IDENTIFY ROBOT IP on your wifi network. Use a tool such as arp-scan on linux or if using a mac laptop, nmap works well. Substitute in your network details.
arp-scan
```
	sudo apt install arp-scan
	sudo arp-scan --interface=wlan0 --localnet
```
nmap
```
	nmap -sn 192.168.0.0/24
```

3) CONNNECT to the robot:  Use a browser to go the robots IP address, for example http://192.168.0.100. 
4) UPDATE FIRMWARE: If you haven't already update firmware on the ICreate, download and install the current [iCreate humble firmware:] (https://iroboteducation.github.io/create3_docs/releases/h_2_6/)

5) PLUG IN PI: Plug the Pi to the USB-C power and data port on the iCreate3. Be sure the USB-BLE mode switch (located near the USB-C port) to BLE in order to enable Bluetooth connections.

6) PAIR BLUETOOTH: Pair the Pi with the robot over bluetooth using the Pi Bluetooth manager. You should see the robot with the name you entered above. If you have difficulties see guidance online for troubleshooting the specific bluetooth manager for your pi hardware/software combo. 

# DETAILED PI INSTALL INSTRUCTIONS:
The following are our setup notes to create a fully configured SD card of Ubunto 22.04.03 for use with the PIHUB framework and optionally ROS2. 

## UBUNTU 22.04 INSTALLATION for PI 4B
1) Install Ubuntu 22.04.03 64 bit LTS using raspberry imager. Install desktop to allow for VNC access and easy wifi and bluetooth configuration. 

2) Use advanced config of the imager to set initial wifi, user name / password. If it doesn't take the guidance in step 3 may assist to edit the card before initial boot. 

3) BEFORE INITIAL BOOT EDIT THE FOLLOWING FILES ON THE CARD:

   * In the system-boot partition, edit config.txt to add at the end of the file:
   ```
   dtoverlay=dwc2,dr_mode=peripheral
   ```
   * In the system-boot partition, edit cmdline.txt to add after rootwait:
   ```
   modules-load=dwc2,g_ether
 	``` 
	* In the system-boot partition, edit the network-config executable to add information about additional Wi-Fi connections
 
4) BOOT PI INITIALLY and update:
```
	sudo apt update && sudo apt upgrade
```

5) Install raspi-config to easily allow easy I2C, SPI, GPIO config. Some distributions may not support this. 
```
	sudo apt-get update && sudo apt-get install raspi-config
```

* If repository not found add and re-run the install
```
	echo "deb http://archive.raspberrypi.org/debian/ buster main" >> /etc/apt/sources.list
hkp://keyserver.ubuntu.com:80 --recv-keys 7FA3303E
```

* once complete run raspi-config, and enable I2C, SPI, Bluetooth, VNC, GPIO
```
		sudo raspi-config
```

7) LOCALE: Set Locale
```
	sudo apt update && sudo apt install locales
	sudo locale-gen en_US en_US.UTF-8
	sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
	export LANG=en_US.UTF-8
```

8) NTP: Setup NTP on this compute board so the Create 3 can sync its clock. Run timedatectl and see if System clock synchronized returns yes.  If not, setup NTP:
 * Install NTP:
```
 	sudo apt install chrony
 	sudo chronyc clients
 ```
 This allows the robot to sync to the pi clock if connected over USB, and the NTP service of the robot is set to the Pi's USB0 address.
 * Specify an NTP server. 

 ```
 	sudo nano /etc/systemd/timesyncd.conf
 ```
 	then add the below contents (or an NTP server of your choice), 
 ```
 	[Time]
 	NTP=ntp.ubuntu.com
 	FallbackNTP=0.us.pool.ntp.org 1.us.pool.ntp.org
 ```
to enable 
 ```
 	systemctl restart systemd-timesyncd.service
 ```

9) PYTHON SETUP: Install required python libraries. Note some distributions may need to use the adafruit blinka install instructions)

REQUIRED PACKAGES:
```
	pip3 install irobot_edu_sdk
	pip3 install python-osc
	pip3 install adafruit-circuitpython-pca9685
	pip3 install adafruit-blinka 
	pip3 install adafruit-circuitpython-servokit
```
SUGGESTED: use a python virtual environment
```
	sudo apt install --upgrade python3-setuptools
```

10) EDIT UFW RULES to allow SSH and UDP to / from devices on the LAN. You may wish to configure other UFW rules as appropriate to your network needs at the this time. These rules assume a secured local network, and adapt IP ranges as appropriate.
```	
		sudo ufw allow ssh
		sudo ufw allow in proto udp from 192.168.0.0/24  
		sudo ufw allow in proto udp from 192.168.186.0/24
		sudo ufw allow in proto udp to 192.168.186.0/24
		sudo ufw allow in proto udp to 192.168.0.0/24
		sudo ufw reload
```
11) PAIR ROBOT via BLUETOOTH: Using the Bluetooth Manager (typically Bluez and Blueman on Ubuntu 22) pair the robot and Pi. In general many pairing issues can be resolved via disabling / enabling the Bluetooth systemctl, and power cycling the iCreate. But, more indepth Bluetooth troubleshooting often requires device specific research.


## OPTIONAL 
12) ADD ADDITIONAL NETWORKS: Once complete with required steps you may wish to configure additional wifi and wired networks you will use the Pi on while still having a monitor, keyboard, mouse connected. 

13) EXTERNAL AUDIO SETUP: If using I2S audio follow OS specific guidance to install the appropriate components. If using the Adafruit MAX98537 board follow the [Adafruit / PhatdDAC tutorial](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/raspberry-pi-usage).


14) PIHUB SUPPORT: In order to run the PIHUB sequencer Clojure and Leiningen are additional requirements. 
* Install Clojure -  [Clojure instructions](https://clojure.org/guides/install_clojure) including installation of prerequisites such as Java.
* Install [Lein](https://leiningen.org/#install)
* TO DO - add Lein and Clojure install scripts

15) VNC FOR HEADLESS USAGE: If you did not install a desktop, and are using a low power device such as a Pi Zero 2 W you may want to install a desktop manager to allow a VNC connection to the Pi. Details can vary greatly depending on device and OS. In general 

Prevent Wayland from use
```
   sudo nano /etc/gdm3/custom.conf
   Uncomment “WaylandEnable=false”
```

THEN - to use the Pi headless:
```
	sudo nano /boot/firmware/config.txt
```
add the following lines
```	
	hdmi_force_hotplug=1
	hdmi_force_mode=1
	hdmi_group=2
	hdmi_mode=82
	#dtoverlay=vc4-kms-v3d
```
Finally install xfce or other desktop manager of your choice

# OPTIONAL ROS2 SETUP - NOT REQUIRED FOR USE WITH BLUETOOTH SDK. HAS EXTREME LATENCY ISSUES USING ROS ACTIONS ON THE ICREATE. 

## CONFIGURE THE PI USING [ICREATE ROS2 GUIDE](https://iroboteducation.github.io/create3_docs/setup/pi4humble/), and the [ROS2 DEBIAN SETUP GUIDE](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html):

The following are highlights of the two guides above.
1) ENABLE USB ETH0 on the Pi and set ICreate Bluetooth mode switch
	* In order to use ROS2 the Pi must be connected to the ICreate compute board in USB mode as opposed to Bluetooth. Details may vary depending on OS version. 
		* edit `etc/netplan/50-cloud-init.yaml`
		* add the following under ethernets after the eth0, matching exactlhy the eth0 indentations 
```			
			usb0:
            addresses:
            - 192.168.186.3/24
            dhcp4: false
            optional: true		
```
```		
		sudo netplan apply
```
Finally, turn the USB-Bluetooth mode switch on the ICreate to USB, connect the Pi and reboot the iCreate application and the Pi.


2) SETUP SOURCES
```	
	sudo apt install software-properties-common
	sudo add-apt-repository universe
```
```
		sudo apt update && sudo apt install curl -y
		sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
```
```
		echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

3) INSTALL ROS 2 HUMBLE
Follow ROS2 [instructions here](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html)

With adaptations for Icreate3 [here]
(https://iroboteducation.github.io/create3_docs/setup/pi4humble/)

Highlights:
```
		sudo apt update && sudo apt install -y curl gnupg2 lsb-release build-essential git cmake
```
		sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
		echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```
```
		sudo apt update
```
		sudo apt install -y ros-humble-desktop
		sudo apt install -y ros-humble-irobot-create-msgs
		sudo apt install -y build-essential python3-colcon-common-extensions python3-rosdep ros-humble-rmw-cyclonedds-cpp
```
		echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

		echo "export RMW_IMPLEMENTATION=rmw_fastrtps_cpp" >> ~/.bashrc
```
```
**Before running ROS2 you must always first run the setup bash script.**
		* `source /opt/ros/humble/setup.bash`

