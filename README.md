# Fill your Boots: Enhanced Embedded Bootloader Exploits via Fault Injection and Binary Analysis

This repository contains source code and data to reproduce results from our paper "Fill your Boots: Enhanced Embedded Bootloader Exploits via Fault Injection and Binary Analysis" at [CHES2021](https://ches.iacr.org/2021/)



## Abstract
The bootloader of an embedded microcontroller is responsible for guarding the device’s internal (flash) memory, enforcing read/write protection mechanisms. Fault injection techniques such as voltage or clock glitching have been proven successful in bypassing such protection for specific microcontrollers, but this often requires expensive equipment and/or exhaustive search of the fault parameters. When multiple glitches are required (e.g., when countermeasures are in place) this search becomes of exponential complexity and thus infeasible. Another challenge which makes embedded bootloaders notoriously hard to analyse is their lack of debugging capabilities.This paper proposes a grey-box approach that leverages binary analysis and advanced software exploitation techniques combined with voltage glitching to develop a powerful attack methodology against embedded bootloaders. We showcase our techniques with three real-world microcontrollers as case studies: 1) we combine static and on-chip dynamic analysis to enable a Return-Oriented Programming exploit on the bootloader of the NXP LPC microcontrollers; 2) we leverage on-chip dynamic analysis on the bootloader of the popular STM8 microcontrollers to constrain the glitch parameter search, achieving the first fully-documented multi-glitch attack on a real-world target; 3) we apply symbolic execution to precisely aim voltage glitches at target instructions based on the execution path in the bootloader of the Renesas 78K0 automotive microcontroller. For each case study, we show that using inexpensive, open-design equipment, we are able to efficiently breach the security of these microcontrollers and get full control of the protected memory, even when multiple glitches are required. Finally, we identify and elaborate on several vulnerable design patterns that should be avoided when implementing embedded bootloaders.



## Dependencies
We use several open source tools and packages to compile and run code on the targets. 

- [k0dasm](https://github.com/mnaberez/k0dasm): A disassembler for the 78k0 
- [as78k0](http://shop-pdp.net/ashtml/as78k0.htm): A compiler for the 78k0
- [aslink](http://shop-pdp.net/ashtml/aslink.htm): A linker for the 78k0
- [sdcc](http://sdcc.sourceforge.net/): Compiler for the stm8
- [naken\_asm](https://github.com/mikeakohn/naken_asm): A disassembler for the stm8
- [stm8flash](https://github.com/vdudouyt/stm8flash):  To flash the stm8 firmware

## Running the code
For the voltage glitching, we use a Raspberry pi3B+ to interface with the GIAnT and the chip under test (cf [Glitch setup](glitch_setup.pdf)). The schematics and source for the GIAnT board is located in the [giant-hardware](giant-hardware) folder.



## Directory Organisation
```
├── 78k0: Code for the 78k0 bootloader analysis (including the symbolic execution framework and glitching code)
├── giant-hardware: Hardware schematics for the new GIAnT board
├── giant-python: Python interface for the GIAnT board
├── lpc: Directory containing the LPC exploit
├── stm8: Code for glitching the STM8
├── README.md
```

## Paper artifacts
The table below clarifies how to recreate the results mentioned in the paper.

| Section | Directory | Commands | Comment |
| ------- | --------- | -------- | ------- |
| 3.2 | ```lpc/ROP``` | ```python3 rop.py```| CRP1 bypass with stack overwrite |
| 3.3 | ```lpc/partial_overwrite``` | ```python3 partial_overwrite.py```| CRP1 bypass with partial flash overwrite |
| 4.1 | ```stm8``` | ```make -C bootloader/```<br>```./flash.sh bootloader/bl_dump.hex option_bytes/STM8AF/opt-rop0-bl0.bin stm8a```| This will flash a firmware to the stm8 which dumps the memory space containing the bootloader over UART |
| 4.2 | ```stm8``` | ```make -C profiling/```<br>```./flash.sh profiling/enter_app.hex option_bytes/STM8AF/opt-rop0-bl0.bin stm8a```<br>```python stm8af_glitch profile``` | This flashes the profiling code and introduces glitches triggered on a GPIO pin |
| 4.3 | ```stm8``` | ```python stm8l_glitch partial_attack``` | Run the glitching on the partially protected stm8l MCU. |
| 4.4 | ```stm8``` | ```python stm8af_glitch full_attack```<br>```python stm8l_glitch full_attack```| Runs the double glitch attack on the STM8 MCUs  |
| 5.1 | ```78k0``` | ```make -C bootloader_dump/```<br>```python glitching/renesas_fpi.py program bootloader/dump_bootl.bin``` | Compiles the code for dumping the 78k0 bootloader. Once flashed, it transmits the code over UART |
| 5.3 | ```78k0/path_constraint``` | ```python2 main.py --db testcases/78k0/checksum_handler.p``` | This command generates the equivalence classes for the checksum handler based on the path through the firmware |
| 5.3 | ```78k0/glitching``` | ```python renesas-78k0-glitch.py``` | This script glitches the checksum command for all equivalence classes output by the path_constraint module |
