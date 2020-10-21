# dac.py is a python port of dac.[h,cpp] to control the glitching part of the GIAnT
from spartan6_fpga import spartan6_fpga
from fpga import Commands, Registers, Register_Bits, FPGA_Vars
import logging


class dac:
    '''Controls glitching logic'''

    def __init__(self):
        self.pulses = []

    def setFaultVoltage(self, v):
        ''' Set fault voltage
        :param v Value to set
        '''
        fpga = spartan6_fpga.getInstance()
        fpga.writeRegister(Registers.DAC_V_HIGH.value, v)


    def setNormalVoltage(self, v):
        ''' Set normal voltage
        :param v Value to set
        '''
        fpga = spartan6_fpga.getInstance()
        fpga.writeRegister(Registers.DAC_V_LOW.value, v)

    def setOffVoltage(self, v):
        ''' Set off (inactive) voltage
        :param v Value to set
        '''
        fpga = spartan6_fpga.getInstance()
        fpga.writeRegister(Registers.DAC_V_OFF.value, v)

    def addPulse(self, offset, width, overwrite = 0):
        ''' Add a pulse to the list of pulses to generate
        :param offset Offset in ns with respect to previous pulse/trigger
        :param width Width in ns
        '''
        #logging.debug("Adding pulse at {} μs: width {} μs".format(offset, width))
        fpga = spartan6_fpga.getInstance()
        # Cast the results of these since they are floats
        offset_p = int(fpga.getNsToPoint() * offset)
        width_p = int(fpga.getNsToPoint() * width)

        min_offset = 3
        min_width = 1

        if offset_p <= min_offset:
            logging.warning("Requested delay shorter than minimum, truncating to minimum")
            offset_p = min_offset + 1

        offset_p -= min_offset

        if width_p < min_width:
            logging.warning("Requested width shorter than minimum, truncating to minimum")
            width_p = min_width

        width_p -= min_width

        # add to the list if not overwriting
        if not overwrite:
            self.pulses.append((offset_p, width_p))
        else:
            self.pulses[-1] = (offset_p, width_p)

        # overwrite existing config memory
        mem_end = 2 * len(self.pulses) + 2
        fi_config = mem_end << 16 | 0x0
        self.writeMemory32(0, fi_config)

        # overwrite pulse memory
        for p in range(len(self.pulses)):
            # offset
            self.writeMemory32(p*2+2, self.pulses[p][0])
            # width
            self.writeMemory32(p*2+2+1, self.pulses[p][1])


    def clearPulses(self):
        '''
        Clear pulse memory
        '''
        # clear list
        self.pulses.clear()

        # overwrite existing config memory
        mem_end = 2*len(self.pulses) + 2
        fi_config = mem_end << 16 | 0x0
        self.writeMemory32(0, fi_config)
	

    def writeMemory8(self, addr, v):
        ''' Write 8-bit directly to FI memory
        :param addr 14-bit memory address
        :param v 8-bit value to write
        '''
        fpga = spartan6_fpga.getInstance()

        # set address
        fpga.writeRegister(Registers.FI_ADDR_L.value, addr & 0xff)
        fpga.writeRegister(Registers.FI_ADDR_H.value, (addr >> 8) & 0x7)

        # set data to write
        fpga.writeRegister(Registers.FI_DATA_IN.value, v)

        #write data
        fpga.risingEdgeRegister(Registers.FI_CONTROL.value, Register_Bits.FI_CONTROL_W_EN.value)
        

    def readMemory8(self, addr):
        ''' Read 8-bit directly from FI memory
        :param addr 14-bit memory address to read
        :return Value at addr
        '''
        fpga = spartan6_fpga.getInstance()

        # set address
        fpga.writeRegister(Registers.FI_ADDR_L.value, addr & 0xff)
        fpga.writeRegister(Registers.FI_ADDR_H.value, (addr >> 8) & 0x7)

        # get data
        return fpga.readRegister(Registers.FI_DATA_OUT.value)

         

    def writeMemory32(self, addr, v):
        ''' Write 32-bit directly to FI memory
        :param addr 12-bit memory address (adressing in 32-bit steps)
        :param v 32-bit value to write
        '''
        for b in range(4):
            self.writeMemory8(4*addr + b, (v >> (8*b)) & 0xff)

    def arm(self):
        ''' Arm DAC for fault injection '''
        fpga = spartan6_fpga.getInstance()

        fpga.risingEdgeRegister(Registers.FI_CONTROL.value, Register_Bits.FI_CONTROL_ARM.value)

    def softwareTrigger(self):
        ''' Force (software) trigger '''
        fpga = spartan6_fpga.getInstance()

        fpga.risingEdgeRegister(Registers.FI_CONTROL.value, Register_Bits.FI_CONTROL_TRIGGER.value)

    def getStatus(self):
        ''' Get status
        :return 8-bit status word
        '''
        fpga = spartan6_fpga.getInstance()

        return fpga.readRegister(Registers.FI_STATUS.value)



    def setTriggerEnableState(self, src, state):
        ''' Enable/disable specific trigger source
        :param src Number in trigger control register, e.g., FI_TRIGGER_CONTROL_PIC
        :param state true to enable, false to disable source
        '''
        fpga = spartan6_fpga.getInstance()

        fpga.setBitRegister(Registers.FI_TRIGGER_CONTROL.value, src, state)


    def setTriggerOnFallingEdge(self, state):
        ''' Enable/disable trigger on falling edge
        :param state true to enable, false to disable
        '''
        fpga = spartan6_fpga.getInstance()

        fpga.setBitRegister(Registers.FI_TRIGGER_CONTROL.value, Register_Bits.FI_TRIGGER_CONTROL_INVERT_EDGE.value, state)


    def setEnabled(self, on):
        ''' Set state of DAC
        :param on True to enable DAC, otherwise false
        '''
        fpga = spartan6_fpga.getInstance()

        fpga.setBitRegister(Registers.DAC_CONTROL.value, Register_Bits.DAC_ENABLE.value, on)

    def setTestModeEnabled(self, on):
        ''' Set test mode state of DAC
        :param on True to enable test mode, otherwise false
        '''
        fpga = spartan6_fpga.getInstance()

        fpga.setBitRegister(Registers.DAC_CONTROL.value, Register_Bits.DAC_TEST_MODE.value, on)

    def setRfidModeEnabled(self, on):
        ''' Control RFID mode of DAC, i.e. DAC will be driven by modulated-sine generator output
        :param on True to enable RFID mode, otherwise false
        :note Will disable UTX mode on enable
        '''
        fpga = spartan6_fpga.getInstance()
        if on:
            self.setUtxModeEnabled(0)

        fpga.setBitRegister(Registers.DAC_CONTROL.value, Register_Bits.DAC_RFID_MODE.value, on)

    def setUtxModeEnabled(on):
        ''' Control UTX mode of DAC 
        In this mode, DAC will be switched to off by zero from UTX and left at normal voltage otherwise. Useful e.g. for driving tristate busses + pulse
        :param on True to enable UTX mode, otherwise false
        :note Will disable RFID mode on enable
        '''
        fpga = spartan6_fpga.getInstance()
        if on:
            self.setRfidModeEnabled(0)

        fpga.setBitRegister(Registers.DAC_CONTROL.value, Register_Bits.DAC_UTX_MODE.value, on)
