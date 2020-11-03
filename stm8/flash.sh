#!/bin/sh


if [ $# -ne 3 ]; then
	echo "Usage: $0 flash.hex opt.bin [stm8l|stm8a]"
	exit 1
fi

if [ $3 = "stm8l" ]; then
	MCU="stm8l152?6"
elif [ $3 = "stm8a" ]; then
	MCU="stm8af6266" 
else
	echo "Please select one of stm8a|stm8l as MCU_type"
	exit 1
fi

# Connect the Vcc through relay
echo "26" > /sys/class/gpio/export
sudo chmod -R 775 /sys/class/gpio/gpio26
echo "out" > /sys/class/gpio/gpio26/direction

sleep 0.1

stm8flash -c stlinkv2 -p $MCU -u
stm8flash -c stlinkv2 -p $MCU -s flash -w $1
stm8flash -c stlinkv2 -p $MCU -s opt -w $2

echo "in" > /sys/class/gpio/gpio26/direction
echo "26" > /sys/class/gpio/unexport
