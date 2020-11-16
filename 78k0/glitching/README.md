# Glitching the Renesas 78K0

This directory concerns itself with glitching the renesas 78k0. The source code is organised as follows:

- [renesas\_fpi.py](renesas_fpi.py): contains the code to interface with the on-chip bootloader of the 78k0. In the paper, we use the SPI interface, however the UART interface is also available to communicate with the bootloader
- [renesas-78k0-glitch.py](renesas-78k0-glitch.py): contains the code for the glitching. 


## 78K0 bootloader interface

In [renesas\_fpi.py](renesas_fpi.py) we provide the following functions to interface with the 78K0 bootloader (either over UART or SPI):

- ```get_checksum(addr_st, addr_e)```: this sends a bootloader command to calculate a checksum over the flash memory starting from ```addr_st``` to ```addr_e``` (including). The bootloader restricts checksum calculation to blocks aligned to 0x100 bytes. Thus, to calculate the checksum of the first flash block, issue the following command: ```get_checksum(0, 0xff)```.
- ```verify(addr_st, addr_e, bin_data)```: this sends a bootloader command to verify the flash content from ```addr_st``` to ```addr_e``` and takes a buffer with the expected bytes. Again, the bootloader restricts this command to flash blocks aligned to 0x100 bytes. 


## Glitching the bootloader commands
Use the following function to get the glitch parameters (searching between 970 and 980mus after the trigger) to calculate the checksum over the four bytes starting from flash address ```4```. Trigger the glitch on the first edge of the transmitted bootloader command. Initially, take the offset range anywhere from the end of the command transmission to when the bootloader replies. This is dependent on the baud rate chosen for the serial connection. Typically, the bootloader should reply within ~100mus of the end of the bootloader command transmission.

```
get_glitch_params(lambda: rsas_glitcher.fp.get_checksum(4,7), (970, 980))
```


Since operating frequency heavily depends on the internal oscillator, of which the frequency is often unpredictable at best (should be 8MHz), absolute glitch offsets may differ from chip to chip. However, once one glitch is found, the other addresses in the equivalence class should have the same offset. Moreover, we can predict glitch offsets in different equivalence classes based on Table 3 in the paper. 

