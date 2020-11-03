import logging
import numpy as np

from glitcher import glitcher
from renesas_fpi import *

class rsas_78k0_glitch(glitcher):

    v_norm      =   3
    v_glitch    =   0.4         # glitch voltage of 0.4 

    w_glitch    =   0.09      # 120 ns for the width



    def  __init__(self):
        self.fp = RenesasFlashProgrammer("78k0", RenesasFlashComm.MODE_UART2)
        if self.fp.fp_mode() == -1:
            logging.error("FP mode did not work - please check connections")

        self.start_glitch_offs = 970 # for address zero

        # initialise all GIAnT related functionality
        super(rsas_78k0_glitch, self).__init__()


    def short_checksum(self, addr):
        self.set_voltages(self.v_glitch, self.v_norm, 0)
        logging.info("{:x} -> {}".format(addr, equ_class))
        glitch_o = self.start_glitch_offs


        self.add_pulse(glitch_o, self.w_glitch)
        self.fp.fp_mode(0)
        add = 0
        while add < 20: 
            logging.info("Glitching offset {}".format(glitch_o + add))
            for i in range(50):
                self.arm()
                try:
                    chk = self.fp.get_checksum(addr, addr + 3)
                    print("{}: bingo!".format(glitch_o + add))
                except NoAckError as e:
                    pass
                except ValueError as e:
                    logging.info(e)
                    self.fp.fp_mode(1)
            add += 0.01 # add 10 ns to the glitch
            self.add_pulse(glitch_o + add, self.w_glitch, overwrite = 1)
        
    def get_glitch_params(self, func, offs_params, N = 50, out_f = None):
        if out_f:
            with open(out_f, 'w') as out:
                out.write("v_norm, v_glitch, w_glich, o_glitch, n_succ, n_reset, N\n")
        offset_st, offset_e, = offs_params
        self.add_pulse(offset_st, self.w_glitch)
        for v_glitch in np.arange(0, 2, 0.02):
            self.set_voltages(v_glitch, self.v_norm, 0)
            max_w = 0.15
            for o_glitch in np.arange(offset_st, offset_e, 0.01):
                for w_glitch in np.arange(0.04, max_w, 0.01):
                    self.add_pulse(o_glitch, w_glitch, overwrite = 1)
                    n_succ = 0
                    n_reset = 0
                    for i in range(N):
                        self.arm()
                        try:
                            func()
                            n_succ += 1
                        except NoAckError as e:
                            pass
                        except ValueError as e:
                            self.set_voltages(0, 0, 0)
                            self.set_voltages(v_glitch, self.v_norm, 0)
                            self.fp.fp_mode(0)
                            n_reset += 1
                    if out_f:
                        with open(out_f, 'a') as out:
                            out.write("{},{},{},{},{},{},{}\n".format(self.v_norm, v_glitch, w_glitch, o_glitch, n_succ, n_reset, N))
                    logging.info("{},{},{},{},{},{},{}".format(self.v_norm, v_glitch, w_glitch, o_glitch, n_succ, n_reset, N))
                    # if all attempts resulted in a reset, then skip to the next offset
                    if n_reset == N:
                        max_w = w_glitch - 0.001
                        break
         


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(filename)s:%(funcName)s: %(message)s")
    rsas_glitcher = rsas_78k0_glitch()
    rsas_glitcher.get_glitch_params(lambda: rsas_glitcher.fp.get_checksum(4,7), (970, 980))
