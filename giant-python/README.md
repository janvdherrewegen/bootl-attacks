# GIAnT Python

This directory contains a python3 port of the [GIAnT](sourceforge.net/projects/giant) project. It uses an inexpensive Ztex FPGA an open-source hardware to facilitate voltage glitching. 

# Usage
In order to make the Ztex FPGA available for any user and not just root, copy the [rules](./99-ztex-rules.d) file over to the udev rules directory (/etc/udev/rules.d/). Any user in the group `usb` can access the USB device. 

Run the [dl\_firm.sh](fpga/dl_firm.sh) script to download the GIAnT firmware to the FPGA. Once finished, the GIAnT should be ready to communicate with our python code.


## Example code
The [glitcher](glitcher.py) class provides most necessary functionality to start voltage glitching. The below example creates an instance and arms the GIAnT.


```
# Create a glitcher object which will interface with the HW
gl = glitcher(trigger_falling_edge = 1, v_step = -8) # Create glitcher object which triggers on falling edge, ranging from +4V to -4V

gl.set_voltages(0, 3.3, 0) # Set Vf,Vdd,Voff

gl.add_pulse(50, 0.1) # Add 100ns pulse 50mus after trigger

gl.arm() # Arm the HW

# ... Execute reset / serial command / ... 

gl.add_pulse(100, 0.2, overwrite = 1) # Overwrite original pulse 

```
