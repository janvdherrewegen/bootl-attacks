from abc import ABCMeta, abstractmethod

import cPickle
from arch import instruction

class Extractor:
    '''Abstract Base Class to extract control flow graph information from a disassembler (e.g. Ghidra or IDA).

    '''

    __metaclass__ = ABCMeta

    def __init__(self, arch):
        self.cfgs_todo = []
        self.funcs_done = set()
        self.arch = arch

    def get_all_cfgs(self, ea, filename = None):
        '''Builds a graph of all control flow graphs referenced from a certain function'''
        self.cfgs_todo.append(ea)
        while self.cfgs_todo:
            addr = self.cfgs_todo.pop()
            print hex(addr)
            done = 0
            for cfg in self.funcs_done:
                #if addr >= cfg.st_addr and addr <= cfg.end_addr:
                if addr == cfg.st_addr:
                    done = 1
            if not done:
                print "----------------"
                print "Getting new CFG"
                print hex(addr)
                print "----------------"
                self.funcs_done.add(self.make_cfg(addr))
        for cfg in self.funcs_done:
            print "Func: " + hex(cfg.st_addr)
            print cfg.basic_blocks()
            # adjust references
            for bb in cfg.basic_blocks():
                print bb
                for ins in bb.insns:
                    if ins.type == instruction.TYPE_CALL:
                        for _cfg in self.funcs_done:
                            if _cfg.st_addr == ins.calls:
                                ins.calls = _cfg
        if filename:
            cPickle.dump(funcs_done, open(filename, 'wb'))
        return self.funcs_done

    @abstractmethod
    def make_cfg(self, addr):
        pass

    def get_cfg(self, addr):
        '''Make the control flow graph of a function specified at address addr (long)'''
        for cfg in self.funcs_done:
            if addr == cfg.st_addr:
                return cfg
        return self.make_cfg(addr)
