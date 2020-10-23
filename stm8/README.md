# Glitching the STM8

The scripts in this directory glitch two different versions of the STM8 microcontroller.

## Setup
Desolder the chip onto a breakout board and connect the following pins:

| Pin | Function |
| --- | -------- |
| V<sub>ddA</sub>, V<sub>dd1</sub> | Power pins |
| V<ss> | Ground |
| NRST | Reset |
| USART1\_RX | Bootloader RX |
| USART1\_TX | Bootloader TX |

## Bootloader dump
The [bootloader/](bootloader) directory contains code to dump the bootloader via the STM8 USART interface. We use [sdcc](http://sdcc.sourceforge.net/) to compile the code and [st-util](https://github.com/stlink-org/stlink) to flash it to the MCU. The bootloader binary can be disassembled with [naken\_asm](https://github.com/mikeakohn/naken_asm) as follows

```
naken_util -disasm -stm8 stm8af_bootloader.bin 
```


## Option bytes
The EEPROM contains option bytes which set or clear the bootloader readout protection. Option byte settings are different for the stm8af and stm8l chips. The [option\_bytes/](option_bytes) folder contains the eeprom files which set and clear the respective readout protection features. 

| File | ROP (Readout Protection flag) | BL | Event | \# Glitches |
| ---- | ----------------------------- | -- | ----- | ----------- |
| opt-rop0-bl1.bin | off | on | Bootloader enabled | 0 |
| opt-rop1-bl1.bin | on | on | Bootloader disabled | 1 |
| opt-rop0-bl0.bin | off | off | Bootloader disabled | 1 |
| opt-rop1-bl0.bin | on | off | Full readout protection | 2 |

## Glitching
Use the scripts [stm8af\_glitch.py](stm8af_glitch.py) and [stm8l\_glitch.py](stm8l_glitch.py) to glitch the readout protection.
