# Renesas flash programming interface implementation
from gpiozero import DigitalOutputDevice, SPIDevice
from time import sleep, time
import serial
import logging
import sys
import numpy
import os.path

class InvalidFrameError(ValueError):
    '''Invalid byte at the beginning of the frame'''
    pass

class InvalidHeaderError(ValueError):
    '''Invalid header byte'''
    pass

class InvalidFooterError(ValueError):
    '''Invalid footer byte'''
    pass

class InvalidChecksumError(ValueError):
    '''Checksum is wrong'''
    pass

class NoResponseError(ValueError):
    '''No response received'''
    pass

class NoAckError(ValueError):
    '''Message was received successfully but status was not ACK'''
    pass

class RenesasFlashComm():
    """Handles the communication with the Renesas Flash interface"""
    
    """Which type of V850 are we talking to"""
    TYPE_V850E2 = 0
    TYPE_V850ES = 1
    TYPE_RH850 = 2
    TYPE_78K0 = 3
    TYPE_D76F = 4
    TYPE_78K0R = 5

    """Communication mode""" 
    MODE_SPI = 0
    MODE_UART2 = 1          # standard 2 wire UART
    MODE_UART1 = 2          # 1 wire UART such as on the 78K0R

    GPIO_FLMD = 2
    GPIO_RESET = 22


    """
        Minimum times necessary for the Flash Programming interface to be ready
        Dependent on Renesas chip 
    """
    RESET_OFF_TIME              = 0.1
    RESET_TIME                  = 0.0056
    RESET_CMD_TIME              = 0.01
    POST_FLMD                   = 0.1


    v850_types = {"v850e2" : TYPE_V850E2, "v850es" : TYPE_V850ES, "rh850": TYPE_RH850, "78k0": TYPE_78K0, "78k0r" : TYPE_78K0R, "d76f": TYPE_D76F}

    """Amount of pulses required on FLMD0 for the serial protocol"""
    flmd_pulses = {TYPE_D76F: {MODE_SPI: 0}, TYPE_RH850: {MODE_SPI: 3, MODE_UART2: 0}, TYPE_V850E2: {MODE_SPI: 8}, TYPE_V850ES: {MODE_UART2: 0, MODE_SPI: 9}, TYPE_78K0: {MODE_UART2: 3, MODE_SPI: 8}, TYPE_78K0R: {MODE_UART2: 0}}


    def __init__(self, v850_type="V850E2", comm_mode = MODE_SPI):
        v850_type = v850_type.lower()
        if v850_type in self.v850_types:
            self.type = self.v850_types[v850_type] 
        else:
            raise ValueError("Did not recognise V850 type")
        print("Starting the flash programming interface for " + v850_type)
        print("----------------------------------------")
        print("FLMD0: GPIO{}\t MISO: 21\t MOSI: 19".format(self.GPIO_FLMD))
        print("RESET: GPIO{}\t CLK: 23".format(self.GPIO_RESET))
        print("----------------------------------------")
        # FLMD0 is GPIO2, RESET is GPIO22
        self.flmd0 = DigitalOutputDevice(self.GPIO_FLMD, initial_value=1)
        self.reset = DigitalOutputDevice(self.GPIO_RESET, initial_value=0)
        self.comm_mode = comm_mode
        if comm_mode == self.MODE_SPI:
            # SPIdev to communicate over the flash programming interface
            self.spicomm = SPIDevice(port=0, device=0)
            # Configure SPI device
            self.spicomm._spi._set_clock_mode(3)
            self.spicomm._spi._interface.max_speed_hz = 10000
            self.serial_port = None
        elif comm_mode == self.MODE_UART2 or comm_mode == self.MODE_UART1:
            ser_port = '/dev/ttyAMA0'
            self.serial_port = serial.Serial(ser_port, 115200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=0.1)
        """Frame bytes"""
        self.FRAME_SOH = 0x01 
        self.FRAME_ETB = 0x17 
        self.FRAME_ETX = 0x03
        # For some reason the V850E2 works differently
        if self.type == self.TYPE_V850E2:
            self.FRAME_STX = 0x11 
        # For all other devices, observed STX was 0x2
        else:
            self.FRAME_STX = 0x02 

        
    def set_timings(self, rst_off, rst_time, rst_cmd, post_flmd):
        '''Sets the timing parameters for the flash programming interface'''
        self.RESET_OFF_TIME = rst_off
        self.RESET_TIME = rst_time
        self.RESET_CMD_TIME = rst_cmd
        self.POST_FLMD = post_flmd

    
    def normal_mode(self):
        '''Operate in normal mode'''
        self.flmd0.off()
        self.reset.on()

    def mcu_off(self):
        '''Turns off reset'''
        self.reset.off()
        self.flmd0.off()



    def fp_uart2(self):
        # pull reset low to restart
        self.reset.off()
        self.flmd0.on()

        sleep(self.RESET_OFF_TIME)

        # pull reset up
        self.reset.on()
        
        # recommended value is 0.0056
        sleep(self.RESET_TIME)

        # pulse FLMD0 an amount of times to set SPI mode
        logging.debug("pulsing FLMD {} times".format(self.flmd_pulses[self.type][self.comm_mode]))
        pulses = self.flmd_pulses[self.type][self.comm_mode]

        for i in range(pulses):
            self.flmd0.off()
            self.flmd0.on()

        self.flmd0.on()

        # wait for RESET command processing ! IMPORTANT do not remove - and if does not work, then fiddle with timing !
        sleep(self.RESET_CMD_TIME)

        if self.comm_mode == self.MODE_UART2:
            self.send([0x00])
            sleep(0.0001)
            self.send([0x00])

        sleep(self.POST_FLMD)


    def reset_fp(self):
        """Enters the renesas flash programming mode and selects the serial communication"""
        logging.debug("Resetting the microcontroller and entering programming mode")

        if self.serial_port:
            self.serial_port.reset_input_buffer()

        # if we are working with the 78K0R (one wire UART over TOOL0)
        if self.comm_mode == self.MODE_UART1:
            self.fp_tool0()
        else:
            self.fp_uart2()


    def checksum(self, data):
        s = 0
        for b in data:
            s = (s - b) & 0xff
        return s & 0xff

    def send(self, data):
        """Sends the buffer with data over the serial interface. """
        # Split data into two parts: up untill the trigger byte and then the rest
        if self.comm_mode == self.MODE_SPI:
            for b in data:
                self.spicomm._spi.transfer(data)
                sleep(0.001)
        elif self.comm_mode == self.MODE_UART2:
            self.serial_port.write(bytearray(data)) 
        elif self.comm_mode == self.MODE_UART1:
            self.serial_port.reset_input_buffer()
            self.serial_port.write(bytearray(data)) 
            #self.serial_port.stopbits = serial.STOPBITS_TWO
            # read back the bytes we sent since it's a single wire
            b_recv = 0
            while b_recv < len(data):
                b = self.serial_port.read(1)
                if b:
                    logging.debug(b)
                    b_recv += 1


    def recv(self, n_bytes):
        """Receives data over the serial interface"""
        if self.comm_mode == self.MODE_SPI:
            return self.spicomm._spi.transfer([0x00 for i in range(n_bytes)])
        elif self.comm_mode == self.MODE_UART2 or self.comm_mode == self.MODE_UART1:
            return self.serial_port.read(n_bytes)


    def print_data(self, data):
        logging.warning(' '.join('{:02x}'.format(x) for x in data))


    def recv_data_frame(self):
        # get header first - 2 bytes for V850ES
        if self.type == self.TYPE_V850E2:
            # 3 bytes for V850E2
            data = self.recv(3)
            d_len = (data[1] << 0x8) + data[2]
        else: 
            data = self.recv(2) 
            if len(data) < 2:
                raise InvalidFrameError("Didn't receive a frame")
            d_len = data[1]
            if d_len == 0:
                d_len = 256

        if data[0] != self.FRAME_STX:
            b = self.recv(1)
            i = 0
            while i < 0x20:
                data +=  b
                i += 1
                b = self.recv(1)
            raise InvalidHeaderError("Received frame is not a data frame: " + " ".join(['{:02x}'.format(b) for b in data]))
        data = data + self.recv(d_len + 2)
        if data[-1] != self.FRAME_ETB and data[-1] != self.FRAME_ETX:
            raise InvalidFooterError("Format error in footer"+ " ".join(['{:02x}'.format(b) for b in data]))
        chk = self.checksum(data[1:-2])
        if data[-2] != chk:
            raise InvalidChecksumError("Incorrect checksum"+ " ".join(['{:02x}'.format(b) for b in data]))
        logging.debug(' '.join('{:02x}'.format(x) for x in data))
        if self.type == self.TYPE_V850E2:
            return data[3:-2]
        else:
            return data[2:-2]

    def make_frame(self, header, data):
        # for v850es
        if self.type == self.TYPE_V850E2:
            l = len(data)
            d = [header, (l >> 8) & 0xff, l & 0xff]
        else:
            d = [header, len(data) & 0xff]
        d = d + data
        d.append(self.checksum(d[1:]))
        d.append(self.FRAME_ETX)
        return d


    def send_command_frame(self, cmd, data = []):
        """Sends a command to the chip
        """
        data_bytes = [cmd] + data
        d = self.make_frame(self.FRAME_SOH, data_bytes)
        logging.debug(' '.join('{:02x}'.format(x) for x in d))
        self.send(d)

    def send_data_frame(self, data=[]):
        d = self.make_frame(self.FRAME_STX, data)
        logging.debug(' '.join('{:02x}'.format(x) for x in d))
        self.send(d)


        
class RenesasFlashProgrammer():
    """Implements the Renesas flash programming interface"""

    COMMAND_RESET                = 0x00
    COMMAND_VERIFY               = 0x13
    COMMAND_19                   = 0x19
    COMMAND_CHIP_ERASE           = 0x20
    COMMAND_BLOCK_ERASE          = 0x22
    COMMAND_BLOCK_BLANK_CHECK    = 0x32
    COMMAND_PROGRAMMING          = 0x40
    COMMAND_READ                 = 0x50
    COMMAND_STATUS               = 0x70
    COMMAND_OSC_FREQUENCY_SET    = 0x90
    COMMAND_BAUD_RATE_SET        = 0x9a
    COMMAND_SECURITY_SET         = 0xa0
    COMMAND_A4                   = 0xa4
    COMMAND_CHECKSUM             = 0xb0
    COMMAND_SIGNATURE            = 0xc0
    COMMAND_VERSION_GET          = 0xc5
    COMMAND_D0                   = 0xd0

    """Status response bytes"""
    STATUS_COMMAND_ERROR     = 0x04
    STATUS_PARAM_ERROR       = 0x05
    STATUS_ACK               = 0x06
    STATUS_CHECKSUM_ERROR    = 0x07
    STATUS_VERIFY_ERROR      = 0x0f
    STATUS_PROTECT_ERROR     = 0x10
    STATUS_NACK              = 0x15
    STATUS_MRG10_ERROR       = 0x1a
    STATUS_MRG11_ERROR       = 0x1b
    STATUS_WRITE_ERROR       = 0x1c
    STATUS_READ_ERROR        = 0x20
    STATUS_BUSY              = 0xff

    def __init__(self, mcu_type = "v850e2", comm_mode = 1):
        self.flashcomm = RenesasFlashComm(mcu_type, comm_mode)
        # 3 bytes per address default
        self.n_bytes = 3
        # should get the timeout in 10ms
        self.timeout = .01
    
    def fp_mode(self, cont = 0):
        '''
            Resets the MCU into flash programming mode and sends the reset command
            Weird construction has to do with the faulting - keep trying until it has succeeded basically
        '''
        ret = self.flashcomm.reset_fp()
        if not cont and ret == -1:
            return -1
        try:
            self.reset_command()
        except (InvalidHeaderError, InvalidFooterError, InvalidChecksumError, NoAckError, InvalidFrameError) as e:
            logging.debug(e)
            logging.debug("FP mode didnt work")
            if not cont:
                return -1
        while cont:
            try:
                self.reset_command()
            except (InvalidHeaderError, InvalidFooterError, InvalidChecksumError, NoAckError, InvalidFrameError) as e:
                logging.debug("Received invalid frame after reset")
                logging.debug(e)
                self.flashcomm.reset_fp()
            else:
                return

    def recv(self):
        '''Receives and returns a dataframe, throws an exception if anything other than an ACK is observed'''
        ret = []
        st = time()
        while not ret and time() < st + self.timeout:
            try:
                ret = self.flashcomm.recv_data_frame()
            except InvalidFrameError as e:
                pass
        if not ret:
            raise InvalidFrameError('Didn\'t receive a frame after timeout')
        if ret[0] == self.STATUS_PARAM_ERROR or ret[0] == self.STATUS_NACK:
            raise NoAckError("Received status {:02x}".format(ret[0]))
        return ret


    def _get_addr_data(self, addr_start, addr_end, n_b = None):
        n_bytes = n_b if n_b is not None else self.n_bytes
        return [(addr_start >> (i*8)) & 0xff for i in range(n_bytes - 1, -1, -1)] + [(addr_end >> (i*8)) & 0xff for i in range(n_bytes - 1, -1, -1)] 



    def get_signature(self):
        self.flashcomm.send_command_frame(self.COMMAND_SIGNATURE)
        # Get status frame
        resp = self.recv()
        # Get signature
        return self.flashcomm.recv_data_frame()

    def reset_command(self):
        self.flashcomm.send_command_frame(self.COMMAND_RESET)
        sleep(0.01)
        return self.recv() 

    def set_frequency(self, freq_data):
        """Sets frequency of the microcontroller (in khz)"""
        self.flashcomm.send_command_frame(self.COMMAND_OSC_FREQUENCY_SET, freq_data)
        return self.recv() 

    def read_memory(self, addr_start, n_bytes):
        """Reads memory from the V850"""
        # n_bytes - 1 because of alignment (need to request 0 - 0xff for example if reading 0x100 bytes)
        data = self._get_addr_data(addr_start, addr_start + n_bytes - 1)
        self.flashcomm.send_command_frame(self.COMMAND_READ, data)
        ret = self.flashcomm.recv_data_frame()
        dat = []
        if ret[0] == 0x6:
            while len(dat) < n_bytes:
                dat += self.flashcomm.recv_data_frame()
                self.flashcomm.send_data_frame([0x6])
        return dat

    def get_version(self):
        self.flashcomm.send_command_frame(self.COMMAND_VERSION_GET)
        resp = self.flashcomm.recv_data_frame()
        return self.recv()

    def get_security(self):
        self.flashcomm.send_command_frame(self.COMMAND_VERSION_GET)
        resp = self.flashcomm.recv_data_frame()
        return self.recv()

    def get_checksum(self, addr_start, addr_end):
        """Gets checksum of a certain address area"""
        data = self._get_addr_data(addr_start, addr_end)
        self.flashcomm.send_command_frame(self.COMMAND_CHECKSUM, data)
        # Get the status frame
        ret = self.recv()
        # Get the actual checksum
        chk = self.recv()
        return (chk[0] << 8) + chk[1]

    def verify(self, addr_start, addr_end, bin_data, ret_early = 0):
        '''Verifies that the data is programmed in the range start_addr:end_addr'''
        self.timeout = 0.1
        data = self._get_addr_data(addr_start, addr_end)
        self.flashcomm.send_command_frame(self.COMMAND_VERIFY, data)
        # Check if ACK received, return for the finding of glitch params
        ret = self.recv()
        while ret[0] == 0x1b:
            ret = self.recv()
        if ret_early:
            return ret
        self.flashcomm.send_data_frame(bin_data)
        return self.recv()

    def program(self, addr_start, bin_data, ret_early = 0):
        '''Programs the binary data to the specified address (in chunks of 0x100 bytes)'''
        self.timeout = 0.1
        # Set the timeout since programming takes longer
        data = self._get_addr_data(addr_start, addr_start + 0xff)
        self.flashcomm.send_command_frame(self.COMMAND_PROGRAMMING, data)
        # Check if ACK received, return for the finding of glitch params
        ret = self.recv()
        if ret_early:
            return ret
        self.flashcomm.send_data_frame(bin_data)
        ret = self.recv()
        return ret


    def block_erase(self, addr_start):
        '''Erases block of 0x100 bytes starting from addr_start'''
        # Align address to a 1kB boundary
        addr_start = addr_start & 0xfffc00
        data = self._get_addr_data(addr_start, addr_start + 0x3ff)
        self.flashcomm.send_command_frame(self.COMMAND_BLOCK_ERASE, data)
        return self.recv()

    def chip_erase(self):
        self.flashcomm.send_command_frame(self.COMMAND_CHIP_ERASE)
        return self.recv()



    def get_checksums(self, start_addr, end_addr):
        '''Gets all (legitimate) checksums from start_addr to end_addr'''
        chks = []
        for i in range(start_addr, end_addr, 0x100):
            chk = fp.get_checksum(i, i + 0xff)
            chks.append(chk)
            print('[{:04x}]: {:04x}'.format(i, chk))
            sleep(0.01)
        return chks


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(filename)s:%(funcName)s: %(message)s")
    fp = RenesasFlashProgrammer("78k0", RenesasFlashComm.MODE_UART2)

    if fp.fp_mode() == -1:
        sys.exit(1)
    signature = fp.get_signature()
    print(" ".join(['{:02x} '.format(i) for i in signature]))
    print(" ".join([chr(i) for i in signature]))
    fp.get_checksum(0x0, 0xff)
    sys.exit(0)

