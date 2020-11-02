import os.path as path
import sys
import logging
import cPickle
import argparse

from cfg import cfg
from rsas_78k0 import Rsas_78K0_Arch
from constraint_solver import constraint_solver
from arch import instruction


parser = argparse.ArgumentParser(description='Constraint class calculation')
parser.add_argument('--db', default = "testcases/78k0/checksum_handler.p", help='Exported database in pickle format')
parser.add_argument('--start_addr', type = lambda x: int(x, 16), default = 0x1aa8, help = "Address of the basic block to start the path search")
parser.add_argument('--end_addr', type = lambda x: int(x, 16), default = 0x1ab7, help = "Address of the last basic block on the path")

args = parser.parse_args()

logging.getLogger().setLevel(logging.ERROR)



START = ['[HL+00h]', '[HL+01h]', '[HL+02h]']
END = ['[HL+03h]', '[HL+04h]', '[HL+05h]']

# The symbolic variables in the path and the values they can assume
VARS = [(START[0], [i for i in range(0x100)]), 
        (START[1], [i for i in range(0x100)]),
        (START[2], [i for i in range(0x100)]),
        (END[0], [i for i in range(0x100)]),
        (END[1], [i for i in range(0x100)]),
        (END[2], [i for i in range(0x100)]),
        ("max_flash_addr_H", [0]),
        ("max_flash_addr_M", [0x1f]),
        ("max_flash_addr_L", [0xff])]


# Extra constraints for setting addr_e = addr_st + 3 (e.g., smallest available checksum)
CONSTR = [(lambda x,y: y-x==3, [START[2], END[2]]), (lambda x,y: x==y, [START[1], END[1]]), (lambda x,y: x==y, [START[0], END[0]])]

# Constraint for to align flash start address to 4 bits: addr_st & 0x3 == 0 ()
CONSTR.append((lambda x: x&3 == 0, [START[2]]))


with open(args.db) as in_f:
    f_cfgs = cPickle.load(in_f)
    for cfg in f_cfgs:
        cfg.arch = Rsas_78K0_Arch()

for cfg in f_cfgs:
    cfg.arch = Rsas_78K0_Arch()
    if cfg.st_addr == args.start_addr:
        # For error code
        for p in cfg.dfs(to_addr = args.end_addr, include_last_blk = 0):
            logging.info("Finding solution for path ...")
            logging.info(p)
            for _p in p.expand():
                c_s = constraint_solver(_p, VARS, CONSTR)
                constraint_solution = c_s.get_constraints()
                if constraint_solution:
                    st_addr = (constraint_solution[START[0]] << 0x10) | (constraint_solution[START[1]] << 0x8) | (constraint_solution[START[2]])
                    e_addr = (constraint_solution[END[0]] << 0x10) | (constraint_solution[END[1]] << 0x8) | (constraint_solution[END[2]])
                    print "Equivalence class {:04x} -> {:04x}: {} ticks".format(st_addr, e_addr, _p.ticks())
                    for _pc in c_s._pretty_constraints:
                        logging.info("{}: {}, {}".format(_pc[0], _pc[1], _pc[2]))
                    logging.debug(_p)
