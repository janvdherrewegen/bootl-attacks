import logging
from arch import instruction

class instruction_path:

    def __init__(self, arch, insns = []):
        self.insns = []
        for ins in insns:
            self.insns.append(ins)
        self.arch = arch

    def __str__(self):
        r = ""
        for ins in self.insns:
            r += "{:<50s}\t{}\n".format(ins, self.arch.ticks(ins))
        return r

    def append(self, ins_path):
        for _i in ins_path.insns:
            self.insns.append(_i)

    def ticks(self):
        cycles = 0
        for ins in self.insns:
            cycles += self.arch.ticks(ins)
        return cycles

class path(object):
    '''This class represents a path of code blocks'''

    def __init__(self, start_cb, arch):
        self.code_blocks = [start_cb]
        self.arch = arch
        self.loops = set()

    def append(self, cb):
        '''Adds a codeblock to the path
        :param cb: the code block to be added to the path
        '''
        self.code_blocks.append(cb)
        return 0

    def pop(self):
        # remove the transition to the last code block
        return self.code_blocks.pop(-1)

    def ticks(self):
        cycles = 0 
        min_cycles_add = 0
        max_cycles_add = 0
        for cb in self.code_blocks:
            for ins in cb.insns:
                if ins.type == instruction.TYPE_CALL:
                    c = ins.calls
                    logging.info("PATH {:x} -> {:x}: calls {:x}".format(self.code_blocks[0].start_ea(), self.code_blocks[-1].start_ea(), c.st_addr))
                    (min_c, max_c) = c.clock_bounds()
                    min_cycles_add += min_c
                    max_cycles_add += max_c
            for insn in cb.insns:
                cycles += self.arch.ticks(insn)
        for loop in self.loops:
            (min_c, max_c) = loop.ticks()
            min_cycles_add += min_c
            max_cycles_add += max_c
        return (cycles + min_cycles_add, cycles + max_cycles_add)

    def contains(self, bb):
        '''returns 1 if path contains basic block'''
        return bb in self.code_blocks

    def __len__(self):
        return len(self.code_blocks)

    def __eq__(self, p):
        '''True if all code blocks come in the same order'''
        if isinstance(p, path):
            eq = True
            if len(self.code_blocks) != len(p.code_blocks):
                return False
            cnt = 0
            for cb in self.code_blocks:
                if cb != p.code_blocks[cnt]:
                    return False
                cnt += 1
            return True
        return False

    def __hash__(self):
        ret_h = 0
        for cb in self.code_blocks:
            ret_h = hash(cb)
        return ret_h


    def __str__(self):
        ret = ""
        for cb in self.code_blocks:
            for loop_path in self.loops:
                if cb == loop_path.code_blocks[0]:
                    ret += "[" + loop_path.__str__() + "] -> "
            ret += hex(cb.start_ea())
            if cb != self.code_blocks[-1]:
                ret +=  " -> "
        return ret

    def expand(self):
        '''Expands the path with all possible paths through all calls'''
        ins_path = instruction_path(self.arch, insns=[])
        paths = [ins_path]
        for cb in self.code_blocks:
            for ins in cb.insns:
                for _p in paths:
                    _p.insns.append(ins)
                # expand the path on a call
                if ins.calls: 
                    # get all calls
                    _t_p = []
                    for _p in ins.calls.dfs(ret_value = 0):
                        _t_p += _p.expand()
                    paths_new = []
                    for _p in paths:
                        # copy the original path to a new path instance
                        for _p2 in _t_p:
                            _p1 = instruction_path(self.arch, _p.insns)
                            _p1.append(_p2)
                            paths_new.append(_p1)
                    paths = paths_new

                    #paths = [_p1.append(_p2) for _p2 in paths for _p2 in _t_p]
                    #print "path_array:"
                    #print paths
                    #print paths[0]
        '''
        print "path at end:"
        print ins_path
        print "PATHS"
        print paths
        '''
        return paths


class loop(path):

    def __init__(self, start_cb, arch):
        super(loop, self).__init__(start_cb, arch)
        # how many times is this loop repeated
        self.loop_n = 0x1

    def ticks(self):
        (min_t, max_t) = super(loop, self).ticks()
        return (self.loop_n * min_t, self.loop_n * max_t)
