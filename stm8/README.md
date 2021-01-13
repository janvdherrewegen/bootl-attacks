# Glitching the STM8

The scripts in this directory glitch two different versions of the STM8 microcontroller:

- STM8L152C6
- STM8AF6266

## Setup
Desolder the chip onto a breakout board and connect the following pins. The chip runs at the standard operating voltage of 3.3V. Other power pins (such as V<sub>ddIO</sub>) can be connected as well, however this will most likely impact the exact glitch voltages (as well as the ambient temperature and other external factors). 

| Pin | Function |
| --- | -------- |
| V<sub>ddA</sub>, V<sub>dd1</sub> | Power pins (connect to the output of the GIAnT) |
| V<sub>ss</sub>, V<sub>ssA</sub> | Ground |
| NRST | Reset (Connect to the GIAnT trigger) |
| USART1\_RX | Bootloader RX |
| USART1\_TX | Bootloader TX |

## Bootloader dump
The [bootloader/](bootloader) directory contains code to dump the bootloader via the STM8 USART interface. We use [sdcc](http://sdcc.sourceforge.net/) to compile the code and [stm8flash](https://github.com/vdudouyt/stm8flash) to flash it to the MCU. The bootloader binary can be disassembled with [naken\_asm](https://github.com/mikeakohn/naken_asm) as follows

```
naken_util -disasm -stm8 stm8af_bootloader.bin 
```

The bootloader dumps are taken from the chips mentioned above. However, we believe at least all chips in the same family (L151x/L152x for the STM8L152C6 and AF62xx for the STM8AF6266) to have the same bootloader. 


## Option bytes
The EEPROM contains option bytes which set or clear the bootloader readout protection. Option byte settings are different for the stm8af and stm8l chips. The [option\_bytes/](option_bytes) folder contains the eeprom files which set and clear the respective readout protection features. 

| File | ROP (Readout Protection flag) | BL | Event | \# Glitches |
| ---- | ----------------------------- | -- | ----- | ----------- |
| opt-rop0-bl1.bin | off | on | Bootloader enabled | 0 |
| opt-rop1-bl1.bin | on | on | Bootloader disabled | 1 |
| opt-rop0-bl0.bin | off | off | Bootloader disabled | 1 |
| opt-rop1-bl0.bin | on | off | Full readout protection | 2 |

## Flash files
The [flash](flash/) directory contains example flash memory files for the three different bootloader paths. Depending on the first byte in memory, the bootloader takes a different path. Note that these files are by no means valid firmware for the stm8, the bootloader only looks at the first byte in flash memory.

| File | Comment |
| ---- | ------- |
| empty\_chip.hex | Considered an empty chip for the bootloader (first byte is not 82 or ac) |
| first\_byte\_ac.hex | "valid" flash file with first byte ac |
| first\_byte\_82.hex | "valid" flash file with first byte 82 |


## Flashing firmware 
To flash firmware onto the device (the stm8a in this case), use the following script. Option bytes files are as described above and located in the [option\_bytes](option_bytes) directory. 

```./flash.sh flash.hex opt.bin stm8a```



## Glitching
To bypass the readout protection, use the code in [stm8af\_glitch.py](stm8af_glitch.py) and [stm8l\_glitch.py](stm8l_glitch.py). The following function can be used to run the glitch profiling when only one glitch is required (cf. option bytes): 

```
state_1_glitch(o_st, o_end, w_st, w_end, v_start, v_end, n_glitches = 2000, o_inc = 0.01, w_inc = 0.01, v_inc = 0.01)
```

To run the full double glitch attack, use the following function:

```
state_2_glitch(state_1_offs, state_2_offs) # Perform the double glitch attack at the given offsets.

```

Note that the glitch voltage and width depend on the ambient temperature, chip manufacturing process and moon phase, hence it is recommended running ```state_1_glitch``` first if performing the attack on a training device.

### Relay
An additional relay was connected and is mentioned in the scripts, which functions as a switch between the programmer (st-link) and our system. This relay ensures any connected devices cannot alter the glitch parameters of the system. 

