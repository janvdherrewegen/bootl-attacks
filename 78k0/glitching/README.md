# Glitching the Renesas 78K0

This directory concerns itself with glitching the renesas 78k0. The source code is organised as follows:

- [renesas\_fpi.py](renesas_fpi.py): contains the code to interface with the on-chip bootloader of the 78k0. In the paper, we use the SPI interface, however the UART interface is also available to communicate with the bootloader
- [renesas-78k0-glitch.py](renesas-78k0-glitch.py): contains the code for the glitching. 

Use the following function to get the glitch parameters (searching between 970 and 980mus after the trigger) for e.g. the checksum command:

```
get_glitch_params(lambda: rsas_glitcher.fp.get_checksum(4,7), (970, 980))
```

Since operating frequency heavily depends on the internal oscillator, of which the frequency is often unpredictable at best (should be 8MHz), absolute glitch offsets may differ from chip to chip. However, once one glitch is found, the other addresses in the equivalence class should have the same offset. Moreover, we can predict glitch offsets in different equivalence classes based on Table 3 in the paper. 
