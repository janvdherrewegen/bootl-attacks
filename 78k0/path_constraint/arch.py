from abc import ABCMeta, abstractmethod, abstractproperty

class instruction():
    ''' Represents an instruction object '''

    TYPE_NORM = 0x0
    TYPE_JMP_COND = 0x1
    TYPE_JMP_UNCOND = 0x2
    TYPE_CALL = 0x3
    TYPE_RET = 0x4

    def __init__(self, mnem, ops, addr, raw_bytes = b''):
        self.mnem = mnem.lower()
        self.ops = ops
        self.addr = addr
        self.raw_bytes = raw_bytes
        self.type = self.TYPE_NORM
        self.calls = None
        self.cond_true = 0 # for conditional branch instructions

    def __str__(self):
        return hex(self.addr) + "\t" + self.mnem + " " + ", ".join(self.ops)



class basic_blk:
    ''' Represents a basic block '''

    def __init__(self, ea = 0):
        '''initialises this basic block'''
        self.insns = []
        self.ea = ea

    def add_insn(self, insn):
        self.insns.append(insn)

    def start_ea(self):
        ''' Returns the first address of this basic block '''
        if self.ea:
            return self.ea
        if self.insns:
            return self.insns[0].addr
        return -1

    def end_ea(self):
        ''' Returns the last address of this basic block '''
        if self.insns:
            return self.insns[-1].addr + len(self.insns[-1].raw_bytes)
        return -1


    def __eq__(self, bb):
        if isinstance(bb, basic_blk):
            return self.start_ea() == bb.start_ea()
        return False

    def __ne__(self, bb):
        return not self.__eq__(bb)

    def __str__(self):
        ret = ""
        for ins in self.insns:
            ret += ins.__str__() + "\n"
        return ret

    def __hash__(self):
        return hash((self.start_ea(), self.end_ea()))

class arch:
    '''Generic class for architectures'''

    __metaclass__ = ABCMeta


    def __init__(self):
        self.instr_set = {}

    @abstractproperty
    def constraint_insns(self):
        pass


    @abstractmethod
    def b_cond(insn):
        pass

    def ticks(self, insn):
        '''Gets the amount of ticks a certain instruction take'''
        try:
            if insn.type == instruction.TYPE_JMP_COND or insn.type == instruction.TYPE_JMP_UNCOND:
                t = self.b_cond(insn)
            else:
                t = self.instr_set[insn.mnem](insn)
        except TypeError as e:
            if insn.mnem in self.instr_set:
                t = self.instr_set[insn.mnem]
        except KeyError:
            raise ValueError("{:x}: Unknown instruction {}".format(insn.addr, insn))
        return t

    def ins_type(self, insn):
        if insn.mnem in self.call_insns:
            return instruction.TYPE_CALL
        elif insn.mnem in self.cond_jump_insns:
            return instruction.TYPE_JMP_COND
        elif insn.mnem in self.uncond_jump_insns:
            return instruction.TYPE_JMP_UNCOND
        elif insn.mnem in self.ret_insns:
            return instruction.TYPE_RET
        return instruction.TYPE_NORM

class DummyArch(arch):

    constraint_insns = []

    def b_cond(insn):
        return 1
