# 78K0 bootloader attack

This directory contains the source material to attack the 78k0 bootloader using our symbolic execution based technique. All experiments are conducted on a 48-pin 78K0/KC2 chip soldered onto a breakout board. 

## Connecting the chip
Desolder the chip onto a breakout board and connect the following pins:

| RPI GPIO | 78K0 Pin | Function |
| -------- | -------- | -------- |
| 23 | RST | Reset |
| 2 | FLMD0 | Bootloader pin |
| 9 | SO | Output from the 78k0 bootloader |
| 10 | SI | Input to the 78k0 bootloader |
| 11 | SCK | SPI clock signal |
| * | REGC | Voltage input to the 78k0 chip (connect to GIAnT output) |
| Vss | Vss | Ground |

## Dumping the bootloader
The ```bootloader_dump``` directory contains the code to dump the bootloader. It sets the necessary registers to map the bootloader in memory and transmits it through the UART.

## Calculating path constraints
The framework to calculate the paths in a command handler and solve the constraints over that path is located in the ```path_constraint``` directory. 

This framework calculates the path constraints from a certain entry point (e.g., the command handler entry) to a certain basic block (e.g., where an error code is set) based on the function control flow graph. Unfortunately, since most versions of IDA and Ghidra only support python2, we have opted to write our code in python2. However, we can port our code to python3 once it is supported by both IDA and Ghidra in the future. 


## Glitching the bootloader
The glitching code is located in the ```glitching``` directory. 
