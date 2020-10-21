# This file contains a Python3 port of the USB logic of the spartan6_fpga
# Author: Jan Van den Herrewegen

import usb.core
import usb.util
import logging, sys

from fpga import Commands, Registers, Register_Bits, FPGA_Vars


class spartan6_fpga:
    """Singleton class spartan6_fpga"""

    __instance = None

    @staticmethod
    def getInstance():
        if spartan6_fpga.__instance is None:
            spartan6_fpga(0x100e6)
        return spartan6_fpga.__instance


    def __init__(self, f_clk, usb_device = None):
        if spartan6_fpga.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            self.f_clk = f_clk
            self.dev = usb_device
            spartan6_fpga.__instance = self

    def getFClk(self): 
        return self.f_clk
	
    def getNsToPoint(self): 
        return self.f_clk/0x1e9

    def __del__(self):
        """Release the USB connection"""
        # TODO write this if necessary?
        pass


    def open(self):
        """Open USB connection"""
        self.dev = usb.core.find(idVendor=0x221a, idProduct=0x100)
        if self.dev is None:
            raise ValueError("Device not found")
        for cfg in self.dev:
            for intf in cfg:
                if self.dev.is_kernel_driver_active(intf.bInterfaceNumber):
                    try:
                        self.dev.detach_kernel_driver(intf.bInterfaceNumber)
                    except usb.core.USBError as e:
                        sys.exit("Could not detach kernel driver")
        self.dev.reset()
        # Configure device with default
        self.dev.set_configuration()
        return 0

    def __exit__(self):
        """Close USB connection"""
        pass


    def resetFpga(self):
        ''' Hardware reset of FPGA
        :return 0 on success, else -1
        ''' 
        logging.debug("Resetting FPGA")
        cmd_buf = [Commands.FPGA_RESET.value]
        self.send_raw_command(cmd_buf)
        response = self.read_result()
        if len(response) == 1 and response[0] == FPGA_Vars.FPGA_SUCCESS.value:
            return 0
        logging.error("Unexpected response: " + ' '.join([hex(b) for b in response]))
        return -1
        

    def readRegister(self, reg):
        ''' Read register of FPGA
        :param reg Register index between FPGA_REG_READ_BEGIN and FPGA_REG_READ_BEGIN + FPGA_REG_READ_COUNT - 1
        :return Value of register
        '''
        if reg >= FPGA_Vars.FPGA_REG_READ_BEGIN.value and reg < FPGA_Vars.FPGA_REG_READ_BEGIN.value + FPGA_Vars.FPGA_REG_READ_COUNT.value:
            cmd_buf = [Commands.FPGA_READ_REGISTER.value, reg]
            self.send_raw_command(cmd_buf)
            response = self.read_result()
            if len(response) == 2 and response[0] == FPGA_Vars.FPGA_SUCCESS.value:
                #logging.debug("Read register {} -> {}".format(reg, response[1]))
                return response[1]
            logging.error("Unexpected response: " + ' '.join([hex(i) for i in response]))
            raise ValueError("spartan6_fpga:readRegister(): unexpected response")
        raise ValueError("Register %d not readable".format(reg))

    def writeRegister(self, reg, value):
        ''' Write register of FPGA
        :param reg Register index between FPGA_REG_WRITE_BEGIN and FPGA_REG_WRITE_BEGIN + FPGA_REG_WRITE_COUNT - 1
        :param value Value to write
        :return 0 on success, else -1
        '''
        if reg >= FPGA_Vars.FPGA_REG_WRITE_BEGIN.value and reg < FPGA_Vars.FPGA_REG_WRITE_BEGIN.value + FPGA_Vars.FPGA_REG_WRITE_COUNT.value:
            cmd_buf = [Commands.FPGA_WRITE_REGISTER.value, reg, value]
            self.send_raw_command(cmd_buf)
            response = self.read_result()
            if len(response) == 1 and response[0] == FPGA_Vars.FPGA_SUCCESS.value:
                return 0
            logging.error("Unexpected response: " + ' '.join([hex(i) for i in response]))
            raise ValueError("spartan6_fpga:writeRegister: unexpected response")
        raise ValueError("writeRegister(): Register %d not writeable".format(reg))

    def writeRegister32(self, reg, value):
        '''Write 32-bit register of FPGA
          :param reg Register index between FPGA_REG_WRITE_BEGIN and FPGA_REG_WRITE_BEGIN + FPGA_REG_WRITE_COUNT - 1
          :param value Value to write
          :note value is clocked in MSByte first
          :return 0 on success, else -1
        '''
        res = 0
        res += self.writeRegister(reg, (value >> 24) & 0xff)
        res += self.writeRegister(reg, (value >> 16) & 0xff)
        res += self.writeRegister(reg, (value >> 8) & 0xff)
        res += self.writeRegister(reg, value & 0xff)
        return res

    def readRegister32(self, reg):
        '''Read 32-bit register of FPGA
            :param reg Register index between FPGA_REG_WRITE_BEGIN and FPGA_REG_WRITE_BEGIN + FPGA_REG_WRITE_COUNT - 1
            :return Value of register
        ''' 
        res = 0
        res |= (self.readRegister(reg) << 0)  & 0x000000ff
        res |= (self.readRegister(reg) << 8)  & 0x0000ff00
        res |= (self.readRegister(reg) << 16) & 0x00ff0000
        res |= (self.readRegister(reg) << 24) & 0xff000000
	
        return res;

    def writeRegister16(self, reg, value):
        '''Write 16-bit shift register of FPGA
            :param reg Register index between FPGA_REG_WRITE_BEGIN and FPGA_REG_WRITE_BEGIN + FPGA_REG_WRITE_COUNT - 1
            :param value Value to write
            :return 0 on success, else -1
        ''' 
        res = 0
        res += self.writeRegister(reg, (value >> 8) & 0xff)
        res += self.writeRegister(reg, value & 0xff)
        return res

    def readRegister16(self, reg):
        '''Read 16-bit register of FPGA
            :param reg Register index between FPGA_REG_WRITE_BEGIN and FPGA_REG_WRITE_BEGIN + FPGA_REG_WRITE_COUNT - 1
            :return Value of register
        ''' 
        res = 0
        res |= (self.readRegister(reg) << 8) & 0x0000ff00
        res |= (self.readRegister(reg)) & 0xff

        return res;

    def risingEdgeRegister(self, reg, bit):
        '''Generate rising edge on bit in a register of FPGA
            :param reg Register index between FPGA_REG_WRITE_BEGIN and FPGA_REG_WRITE_BEGIN + FPGA_REG_WRITE_COUNT - 1
            :param bit Bit to affect
            :return 0 on success, else -1
        ''' 
        if bit < 8:
            curr_state = self.readRegister(reg)
            # clear bit
            curr_state &= ~(1 << bit)
            if self.writeRegister(reg, curr_state) != 0:
                return -1
            # set bit 
            curr_state |= (1 << bit)
            if self.writeRegister(reg, curr_state) != 0:
                return -1
            # clear bit
            curr_state &= ~(1 << bit)
            if self.writeRegister(reg, curr_state) != 0:
                return -1
            return 0
        raise ValueError("risingEdgeRegister(): bit %d out of range".format(bit))

    def setBitRegister(self, reg, bit, v):
        '''  Set/clear bit in register
            :param reg Register index between FPGA_REG_WRITE_BEGIN and FPGA_REG_WRITE_BEGIN + FPGA_REG_WRITE_COUNT - 1
            :param bit Bit to affect
            :param v Value to set
            :return 0 on success, else -1
        ''' 
        logging.debug("spartan6_fpga:setBitRegister %x %d %d", reg, bit, v)
        if bit < 8:
            curr_state = self.readRegister(reg)
            #logging.debug("spartan6_fpga:readRegister: %x", curr_state)
            # clear bit
            if not v:
                curr_state &= ~(1 << bit)
                if self.writeRegister(reg, curr_state) != 0:
                    return -1
            # set bit 
            else:
                curr_state |= (1 << bit)
                if self.writeRegister(reg, curr_state) != 0:
                    return -1
            return 0
        raise ValueError("setBitRegister(): bit %d out of range".format(bit))

    def send_raw_command(self, frame, timeout = 1000):
        '''  Helper to send raw command

        :param frame Raw binary data to send
        :param timeout Timeout in ms
        :return Number of bytes written, -1 on error
        ''' 
        if self.dev is not None:
            bytes_written = self.dev.write(0x4, frame, timeout)
            # Check if all bytes were transferred
            if bytes_written != len(frame):
                raise IOError("USB bulk write failed")
            return bytes_written
        else:
            raise Exception("Device is not connected")
        


    def read_result(self, n_bytes = 256, timeout = 1000):
        '''Read response
        :param timeout Timeout in ms
        :return array of bytes read
        '''
        if self.dev is not None:
            read_bytes = self.dev.read(0x82, n_bytes, timeout)
            # TODO check return value
            if len(read_bytes) == 0:
                raise IOError("USB read failed")
            return read_bytes
        else:
            raise Exception("USB device not connected")

    def read_result_n(self, n, timeout = 200, max_reads = 200):
        '''Read response with n bytes
            :param n Number of bytes expected
            :param timeout Timeout in ms (for a single read!)
            :param max_reads Maximum number of single read attempts, -1 for infinite attempts
            :return array with read bytes
        ''' 
        attemps = 0
        read_bytes = []
        while len(read_bytes) < n and (attempts < max_reads or max_reads < 0):
            try:
                read_bytes = read_bytes + read_result(n, timeout)

            except IOError as err:
                pass
            attemps = attempts + 1
        return read_bytes




if __name__ == "__main__":
    print("spartan6_fpga.py ...")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    fpga = spartan6_fpga.getInstance()
    with fpga as f:
        f.resetFpga()


