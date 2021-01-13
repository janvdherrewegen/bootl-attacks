# GIAnT Hardware

This directory contains the schematics for the revised GIAnT board. In line with the previous version, it still uses the (now deprecated) [ZTEX USB-FPGA Module 1.11](https://www.ztex.de/usb-fpga-1/usb-fpga-1.11.e.html). New adopters can order the following components for an alternative:

- [USB-FPGA Module 2.04](https://www.ztex.de/usb-fpga-2/usb-fpga-2.04.e.html): 99 EUR
- [Series 1 Adapter](https://www.ztex.de/usb-fpga-2/1-adapter.e.html): 8 EUR

Including the PCB and all other components, the hardware can be assembled for ~200 USD. [BOM.txt](BOM.txt) contains a detailed Bill of Materials.

## Specifications
With the original composition, the GIAnT offers the following capabilities:

- 10ns minimum pulse width
- 10ns minimum pulse offset
- 145mA max current draw (limited by the [THS3062](https://www.ti.com/store/ti/en/p/product/?p=THS3062D) opamp)

