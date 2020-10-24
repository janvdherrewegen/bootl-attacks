# NXP LPC1343 CRP bypass
This exploit bypasses CRP level 1 of the LPC1343 through Return-Oriented Programming. 

## Exploit
- Encode the exploit using a UU-encoding tool

- Invoke the UART bootloader

- Call the "Write to RAM" command by sending ```W 268443476 172``` to the bootloader.

- Send the encoded exploit to the device

