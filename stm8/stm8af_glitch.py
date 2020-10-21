from glitcher import glitcher
from gpiozero import DigitalOutputDevice, DigitalInputDevice, Button
import numpy as np

from exceptions import *

from stm8_bootl import stm8_bootloader

import serial

import logging

from time import sleep
import sys

class stm8_glitcher:
    '''Class for glitching the stm8 bootloader'''

    '''GPIO pins to check the result of the glitch'''
    GPIO_PORT_E7 = 27 # bootloader_state = 2 ; entered bootloader


    N_GLITCHES = 1
    V_GLITCH_MAX = 1.5
    W_GLITCH_MAX = 2 # 2 clock ticks max width
    O_GLITCH_MAX = 20 # 30 ticks max offset
    V_NORMAL_MAX = 3.3

    def __init__(self, freq, stm8_chip = "stm8a", sync_bootl = 1):
        ''':param freq: The frequency of the microcontroller (in Hz)'''
        self.glitcher = glitcher()
        self.bootl_if = stm8_bootloader(stm8_chip)
        # For checking the result of the glitch
        # Something strange happens for stm8a: when gpio connected as digital input through the relay - bootloader does not reply. 
        self.sync_bootl = sync_bootl
        if sync_bootl:
            self.bootl_if.gpio_relay.off()
        else:
            self.bootl_if.gpio_relay.on()
            self.port_e = DigitalInputDevice(self.GPIO_PORT_E7)
        self.reset = self.bootl_if.reset
        self.freq = freq 

        self.glitch_offset = 10  # start at 10 cycles
        self.glitch_width = 1.0 # start at 1 clock cycle
        self.glitch_voltage = 1.72
        self.normal_voltage = 3.6 # 1.85 is lowest the STM8 will still run
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



    def undervolt(self):
        self.glitcher.set_voltages(self.glitch_voltage, self.normal_voltage, 0)
    
    def state_1_glitch(self, o_st, o_end, w_st, w_end, v_start, v_end, n_glitches = 2000, o_inc = 0.01, w_inc = 0.01, v_inc = 0.01, sleep_time = 0.000062, ret_value = 1, out_f = None):
        ''' 
            Tries to find glitches to go into state 1
        '''
        self.glitcher.dac.setTriggerOnFallingEdge(0) # for bootloader glitch
        # one initial pulse so we can overwrite
        self.glitcher.clear_pulses()
        self.glitcher.add_pulse(o_st, o_end)
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
                        #self.glitch(offset, width)
                        # offset and width in microseconds
                        self.glitcher.add_pulse(offset, width, overwrite=1)
                        res =  self.test_glitches(n_glitches, sleep_time, ret_value = ret_value, n_succ_glitches = n_glitches) 
                        logging.info("%d glitches success (%f, %f, %f)" % (res, offset, width, f_voltage))
                        if out_f:
                            with open(out_f, 'a') as f:
                                f.write('{:f},{:f},{:f},{},{:f}\n'.format(f_voltage, offset, width, res, self.normal_voltage)) 

        except KeyboardInterrupt as e:
            logging.info("interrupted (%f, %f)" % (offset, width))

    def state_2_glitch(self, state_1_offs = 80.75, state_2_offs = 3.9, sleep_time = 0.00006):
        '''
            Tries to glitch the bootloader readout protection
        '''
        self.glitch_voltage = 2.31
        self.undervolt()
        self.glitcher.dac.setTriggerOnFallingEdge(0) # for bootloader glitch
        state_1_width = 0.120 # 120 ns for 1.84 volt
        state_2_width = 0.120
        while 1:
            glitch_v = self.glitch_voltage
            while glitch_v < self.glitch_voltage + 0.001:
                self.glitcher.set_voltages(glitch_v, self.normal_voltage, 0)
                for state_1_offs in np.arange(state_1_offs, state_1_offs + 0.001, 0.01): # for chip 1
                    self.glitcher.clear_pulses()
                    self.glitcher.add_pulse(state_1_offs, state_1_width)
                    self.glitcher.add_pulse(state_2_offs, state_2_width)
                    for state_2_offs in np.arange(state_2_offs, state_2_offs + 0.1, 0.01):
                        self.glitcher.add_pulse(state_2_offs, state_2_width, overwrite=1)
                        logging.info("[%f V]: state 2 glitches: (%f, %f) (%f, %f)" % (glitch_v, state_1_offs, state_1_width, state_2_offs, state_2_width))
                        n_succ = self.test_glitches(500000, sleep_time)
                        if n_succ > 0:
                            logging.info("Entered bootloader")
                            logging.info("%d glitches success (%f, %f) (%f, %f)" % (n_succ, state_1_offs, state_1_width, state_2_offs, state_2_width))
                glitch_v += 0.01


    def test_glitches(self, n_times, sleep_time, ret_value = 1, n_succ_glitches = 1):
        '''Runs glitches for n_times and checks if port is set high'''
        n_glitches = 0
        # turn off micro
        for i in range(n_times):
            self.reset.off()
            self.glitcher.arm()
            self.reset.on()
            sleep(sleep_time) 
            # stm8a does not work so smoothly with relays and digital input device
            if self.sync_bootl:
                try:
                    self.bootl_if.synchr_bootl()
                    n_glitches += 1
                    logging.info("SUCCESS")
                except NoAckError as e:
                    logging.debug(e)
                if n_glitches > n_succ_glitches:
                    return n_glitches # return early cause of relay!
            # If goes high for 1sec and then low - bootloader active! 
            elif self.port_e.value == ret_value:
                sleep(1.2)
                if self.port_e.value == 0:
                    logging.info("SUCCESS")
                    n_glitches += 1
                else:
                    logging.info("Pin high but no cigar")
                    return 0
        return n_glitches


    
def flash_stm8(flash_f, opt_file):
    import subprocess
    flash_f_dir = "."
    compl_proc = subprocess.run(["./{}/flash.sh".format(flash_f_dir), "{}/{}".format(flash_f_dir,flash_f), "{}/{}".format(flash_f_dir, opt_file)], capture_output=True)
    logging.info(compl_proc.stdout.decode())
    logging.info(compl_proc.stderr.decode())




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(filename)s:%(funcName)s: %(message)s")
    glitcher = stm8_glitcher(2000000, stm8_chip = "stm8a", sync_bootl = 0)
 
    glitcher.state_2_glitch(state_1_offs = 80.75, state_2_offs = 3.9)
