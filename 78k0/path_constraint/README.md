# Constraint-based Glitching

This Proof-of-Concept on the 78k0 bootloader calculates the constraints along all paths through the ```checksum``` command handler. 

## Dependencies
This directory has been tested on the following version of Python:

```
IDAPython v1.7.0 final
Python 2.7.18
```

The [requirements](requirements.txt) file contains the dependencies for the code in this directory.


## Usage
### Loading the database
Load the bootloader binary into IDA on address ```0``` and trigger the auto analysis. For reference, the below table clarifies the memory on several addresses in the firmware. 

| Address | Function | Comments |
| ------- | -------- | -------- | 
| ```0544``` | cmd bytes | Array of static command bytes mapped to a bootloader function on `````` | 
| `````` | handler ptrs | Array of bootloader handler function pointers | 
| ```1aa8``` | ```checksum_handler``` | The checksum command handler function | 

### Exporting handler functions
To provide optimal compatibility with both IDA and Ghidra, we export the database to our own framework. Run the ```ida_exporter.py``` script in IDA to export a handler function (and all subsequent functions it calls) from the database to the format we use. It prompts the user for the function address, and the output file. 

This exports the function located at the specified address and all the functions/subroutines called from within that function to the specified pickle file. 


### Calculating the paths
For reference, we have exported the ```checksum_handler``` function into [checksum_handler.p](testcases/78k0/checksum_handler.p). In order to calculate the paths through this function use the following script. This takes as optional arguments the pickle file, the address of the basic block to search from (e.g., the checksum handler address in this case) and the address of the basic block to search for (e.g., the basic block indicating an error message here) 

```
> python2 test.py testcases/78k0/checksum_handler.p 1aa8 1ab7

Equivalence class 1f00 -> 1f03: 644 ticks
Equivalence class 1e00 -> 1e03: 622 ticks
Equivalence class 0000 -> 0003: 466 ticks
Equivalence class 1ff8 -> 1ffb: 632 ticks
Equivalence class 1ef8 -> 1efb: 610 ticks
Equivalence class 00f8 -> 00fb: 454 ticks
Equivalence class 1ffc -> 1fff: 642 ticks
Equivalence class 1efc -> 1eff: 614 ticks
Equivalence class 00fc -> 00ff: 536 ticks

``` 

