# Fill your Boots: Enhanced Embedded Bootloader Exploits via Fault Injection and Binary Analysis

This repository contains source code and data to reproduce results from our paper "Fill your Boots: Enhanced Embedded Bootloader Exploits via Fault Injection and Binary Analysis" at [CHES2021](https://ches.iacr.org/2021/)



## Abstract
The bootloader of an embedded microcontroller is responsible for guarding the device’s internal (flash) memory, enforcing read/write protection mechanisms. Fault injection techniques such as voltage or clock glitching have been proven successful in bypassing such protection for specific microcontrollers, but this often requires expensive equipment and/or exhaustive search of the fault parameters. When multiple glitches are required (e.g., when countermeasures are in place) this search becomes of exponential complexity and thus infeasible. Another challenge which makes embedded bootloaders notoriously hard to analyse is their lack of debugging capabilities.This paper proposes a grey-box approach that leverages binary analysis and advanced software exploitation techniques combined with voltage glitching to develop a powerful attack methodology against embedded bootloaders. We showcase our techniques with three real-world microcontrollers as case studies: 1) we combine static and on-chip dynamic analysis to enable a Return-Oriented Programming exploit on the bootloader of the NXP LPC microcontrollers; 2) we leverage on-chip dynamic analysis on the bootloader of the popular STM8 microcontrollers to constrain the glitch parameter search, achieving the first fully-documented multi-glitch attack on a real-world target; 3) we apply symbolic execution to precisely aim voltage glitches at target instructions based on the execution path in the bootloader of the Renesas 78K0 automotive microcontroller. For each case study, we show that using inexpensive, open-design equipment, we are able to efficiently breach the security of these microcontrollers and get full control of the protected memory, even when multiple glitches are required. Finally, we identify and elaborate on several vulnerable design patterns that should be avoided when implementing embedded bootloaders.



## Dependencies

## Directory Organisation
```
├── 78k0: Code for the 78k0 bootloader analysis (including the symbolic execution framework and glitching code)
├── giant-hardware: Hardware schematics for the new GIAnT board
├── giant-python: Python interface for the GIAnT board
├── lpc: Directory for the LPC exploit
├── stm8: Code for glitching the STM8
├── README.md
```

## Building and running



