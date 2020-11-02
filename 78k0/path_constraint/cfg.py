import cPickle

from copy import deepcopy
from path import path, loop

import logging

class CfgException(Exception):
    pass

class cfg_db:
    '''Class to store all extracted cfgs'''

    def __init__(self, f_cfgs):
        self.f_cfgs = f_cfgs

    def get_func(self, func_ea):
        for f_cfg in self.f_cfgs:
            if f_cfg.st_addr == func_ea:
                return f_cfg
        raise CfgException("Control flow graph was not in db")

    def cfg(self, ea):
        for cfg in self.f_cfgs:
            if cfg.st_addr == ea:
                return cfg
        return None

class cfg:
    '''Class for a function control flow graph'''

    STATE_UNVISITED = 0
    STATE_VISITED = 1
    STATE_COMPLETE = 2
    

    def __init__(self, arch, st_addr, end_addr = None, cfg_dict = None):
        '''
            :st_addr: Start address of the function
            :end_addr: End address of the function (including this address)
        '''
        if cfg_dict == None:
            cfg_dict = {}
        self.__cfg_dict = cfg_dict
        self.st_addr = st_addr
        self.end_addr = end_addr if end_addr else st_addr
        self.arch = arch

    def basic_blocks(self):
        return self.__cfg_dict.keys()

    def add_bb(self, bb):
        '''Adds basic block to the function cfg'''
        if bb not in self.__cfg_dict:
            self.__cfg_dict[bb] = set()
            if bb.end_ea() > self.end_addr:
                self.end_addr = bb.end_ea()
        else:
            return -1
        return 0

    def add_xref(self, bb1, bb2):
        '''Adds cross reference xref - (from, to) to the cfg'''
        if bb1 in self.__cfg_dict:
            self.__cfg_dict[bb1].add(bb2)
        else:
            self.__cfg_dict[bb1] = set(bb2)
        # Add the second basic block to the dict
        self.add_bb(bb2)
    
    def get_bb(self, addr):
        '''Get basic block that matches a certain address'''
        for bb in self.__cfg_dict.keys():
            logging.info("Looking up bb %x -> %x" % (bb.start_ea(), bb.end_ea()))
            if addr >= bb.start_ea() and addr < bb.end_ea():
                return bb
        raise CfgException("Address %x not in CFG" % (addr))
        
    def visit(self, bb, end_bb):
        ''' Visit a node in DFS '''
        self.states[bb] = self.STATE_VISITED
        logging.debug("Visiting {}".format(hex(bb.start_ea())))
        states_visited = []
        for cb in self.states:
            if self.states[cb] == self.STATE_VISITED:
                states_visited.append(cb)
        logging.debug("States visited: {}".format([hex(s.start_ea()) for s in states_visited]))
        if bb == end_bb:
            # make a hard copy of the list
            self.paths.append(deepcopy(self.path))
        else:
            # Visit all neighbours of this node
            for n in self.__cfg_dict[bb]:
                if self.states[n] == self.STATE_UNVISITED:
                    # set the condition code for branches (important for clock count - if jump taken it can takes more cycles)
                    # TODO make raw_bytes for ida
                    #bb.insns[-1].cond_true = 1 if n.start_ea() != bb.end_ea() + len(bb.insns[-1].raw_bytes) else 0
                    bb.insns[-1].cond_true = 1 if n.start_ea() != bb.end_ea() + 2 else 0

                    self.path.append(n)
                    self.visit(n, end_bb)
                elif self.states[n] == self.STATE_VISITED:
                    logging.debug("Cycle %x from %x" % (n.start_ea(), bb.start_ea()))
                    logging.debug(self.path)
                    loop_path = loop(n, self.arch)
                    append = 0
                    for cb in self.path.code_blocks:
                        if append:
                            loop_path.append(cb)
                        if cb == n:
                            append = 1
                        if cb == bb:
                            break
                    logging.debug("Cycle path: ")
                    logging.debug(loop_path)
                    self.loops.add(loop_path)
        p = self.path.pop()
        logging.debug("Done visiting {}".format(hex(bb.start_ea())))
        self.states[bb] = self.STATE_UNVISITED

    def dfs(self, from_addr = None, to_addr = None, ret_value = None, include_last_blk = 1):
        if not from_addr:
            from_addr = self.st_addr
        # get the Basic blocks to which the addresses belong
        from_bb = self.get_bb(from_addr)
        # Either search for a specific block, or if not specified, search for all return blocks
        if to_addr:
            t_bb = [self.get_bb(to_addr)]
        else:
            t_bb = self.last_blks(ret_value)

        logging.debug("Getting all paths from {} to {}".format(hex(from_bb.start_ea()), [hex(to_bb.start_ea()) for to_bb in t_bb]))

        self.paths = []
        self.loops = set()
        for to_bb in t_bb:
            self.states = {}
            self.parent = {}
            for bb in self.__cfg_dict.keys():
                self.states[bb] = self.STATE_UNVISITED
            self.path = path(from_bb, self.arch)
            self.visit(from_bb, to_bb)

        # add the possible loops to the paths
        for p in self.paths:
            for l in self.loops:
                if p.contains(l.code_blocks[0]):
                    p.loops.add(l)

        logging.debug("Got all paths from {} to {}".format(hex(from_bb.start_ea()), [hex(to_bb.start_ea()) for to_bb in t_bb]))
        for p in self.paths:
            logging.debug(p)
            if not include_last_blk:
                p.code_blocks.pop()
        return self.paths

    def clock_bounds(self):
        '''Calculates the clock bounds of this cfg
        :return (min, max): the minimum and maximum amount of ticks this cfg will take (including calls to other functions/subroutines)
        '''
        min_ticks = 10000000
        max_ticks = 0
        for path in self.dfs():
            (b_min, b_max) = path.ticks()
            min_ticks = min(min_ticks, b_min)
            max_ticks = max(max_ticks, b_max)
        return (min_ticks, max_ticks)

                    

    def last_blks(self, ret_value = None):
        '''Retrieves the return block(s) (i.e. blocks with out-degree zero) of this cfg'''
        ret_blocks = [bb for bb in self.__cfg_dict if not self.__cfg_dict[bb]]
        if ret_value == None or len(ret_blocks) == 1:
            return ret_blocks
        r_b = []
        # Get the most common instructions to indicate success / failure in a function
        ins_to_search = self.arch.success_insns if ret_value == 0 else self.arch.error_insns
        for ins in ins_to_search:
            for ret_block in ret_blocks:
                for i in ret_block.insns:
                    if ins == i.mnem:
                        r_b.append(ret_block)
        return r_b


    def __str__(self):
        ret = ""
        for bb in self.__cfg_dict:
            ret += hex(bb.start_ea()) + "-> " + ", ".join([hex(bb2.start_ea()) for bb2 in self.__cfg_dict[bb]]) + "\n"
        return ret

    def __eq__(self, f_cfg):
        if isinstance(f_cfg, cfg):
            return self.st_addr == f_cfg.st_addr and self.end_addr == f_cfg.end_addr
        return False

    def __ne__(self, f_cfg):
        return not self.__eq__(f_cfg)

    def __hash__(self):
        return hash((self.st_addr, self.end_addr))

