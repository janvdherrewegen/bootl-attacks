from spartan6_fpga import spartan6_fpga
from fpga import Commands, Registers, Register_Bits, FPGA_Vars
from dac import dac


class glitcher:
    '''Generic class that interfaces with the GIAnT HW'''

    
    def __init__(self, trigger_falling_edge = 1, v_step = -8):
        '''Initialise the GIAnT HW
            :trigger_falling_edge: Sets the trigger on falling edge (1) or rising edge (0)
            :v_step: Voltage step - specify the range on the GIAnT hardware. Here +4V to -4V
        '''
        # create dac object
        self.dac = dac()
        # init singleton instance
        self.fpga = spartan6_fpga.getInstance()

        # Initialise FPGA
        self.reset_fpga()

        self.dac.setTestModeEnabled(0)
        self.dac.setRfidModeEnabled(0)

        self.dac.clearPulses()
        self.dac.setTriggerEnableState(Register_Bits.FI_TRIGGER_CONTROL_EXT1.value, 0)

        # Default trigger on falling edge - set this to zero
        self.dac.setTriggerOnFallingEdge(1)
        # Set the trigger to external
        self.dac.setTriggerEnableState(Register_Bits.FI_TRIGGER_CONTROL_EXT1.value, 1)

        self.V_STEP = v_step/256


    def calc_voltage(self, v):
        '''Calculates the value to write to the GIAnT for the voltage'''
        return int(v/self.V_STEP + 128)

    def set_voltages(self, f_voltage, norm_voltage, off_voltage):
        '''Write the voltages to the GIAnT 

        :param f_voltage: the fault voltage (in V - e.g. 1.8V)
        :param norm_voltage: the normal voltage (e.g. 3.3V)
        :param off_voltage: the off voltage (e.g. 0V)
        '''
        v_normal = self.calc_voltage(norm_voltage)
        v_off = self.calc_voltage(off_voltage)
        v_fault = self.calc_voltage(f_voltage)

        # Set voltages
        self.dac.setFaultVoltage(v_fault)
        self.dac.setNormalVoltage(v_normal)
        self.dac.setOffVoltage(v_off)

    def set_f_voltage(self, f_voltage):
        '''Calculates and sets only the fault voltage'''
        v_fault = self.calc_voltage(f_voltage)
        self.dac.setFaultVoltage(v_fault)

    def add_pulse(self, offset, width, overwrite = 0):
        '''Sets the width and offset of a pulse - given in microseconds
        
        :param width: width of the pulse (in microseconds)
        :param offset: offset from the trigger (in microseconds)
        '''
        # For some reason the width and offset are off by 1.32, so convert them from microseconds
        w = width/1.33
        o = offset/1.33
        # Set a pulse
        self.dac.addPulse(o, w, overwrite)

        
          
    def test_mode(self):
        '''
            Enables the test mode on the GIAnT - Voltage goes from highest possible to lowest possible
        '''
        self.reset_fpga()
        self.dac.setTestModeEnabled(1)

    def reset_fpga(self):
        '''
            Resets the FPGA connection
        '''
        # Open USB connection
        self.fpga.open()
        self.fpga.resetFpga()

        # Enable the DAC 
        self.dac.setEnabled(1)


    def test_fi(self):
        '''
            tests the Fault Injection on the FPGA. Adds two pulses, sets a software trigger and arms the FPGA
        '''
        self.reset_fpga()
        self.dac.setTestModeEnabled(0)
        self.dac.setRfidModeEnabled(0)

        self.set_voltages(1, 3.3, 0)

        self.dac.clearPulses()

        # Set a pulse
        self.add_pulse(100, 20)
        self.add_pulse(100 + 30, 20)

        # Arm the DAC
        self.dac.arm()

        # Generate a software trigger
        self.dac.softwareTrigger()  

    def clear_pulses(self):
        '''Clears all pulses in the dac'''
        self.dac.clearPulses()

    def arm(self):
        '''
            Arm the dac - will insert a glitch when trigger pin goes high
        '''
        self.dac.arm()




if __name__ == "__main__":
    glitcher = glitcher()
    glitcher.test_fi()
