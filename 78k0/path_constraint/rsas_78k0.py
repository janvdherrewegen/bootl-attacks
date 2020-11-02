import re
import collections
from arch import arch

class Rsas_78K0_Arch(arch):
    '''
        Instruction set for the 78K0 architecture. Clock ticks are slightly simplified - since many options depend on whether in RAM etc, or whether operating on register / address / ...
    '''

    def is_reg(self, opn):
        return re.match("[AXBCDEHL]", opn) is not None

    def is_const(self, opn):
        return re.match("#.*h", opn) is not None

    def b_cond(self, insn):
        '''
            br AX: 8 ticks 
            all other branches are 6 ticks
        '''
        if "AX" in insn.ops[0]:
            return 8
        return 6
            
    def simple_arithmetic(self, insn):
        if self.is_reg(insn.ops[0]):
            return 2
        return 4

    def bitwise_op(self, ins):
        ''' For operations such as set1, clr1, ... '''
        opn = ins.ops[0]
        if re.match("CY", opn) is not None:
            return 2
        else:
            return 4

    def mov(self, insn):
        ''' For mov instructions '''
        if self.is_reg(insn.ops[0]):
            op_2 = insn.ops[1]
            if self.is_const(op_2):
                return 4
            if re.match("!", op_2) is not None or re.match("\[HL+", op_2) is not None:
                return 8
            else:
                return 4
        elif self.is_reg(insn.ops[1]):
            ''' mov xx, A '''
            op_1 = insn.ops[0]
            if re.match("!", op_1) is not None or re.match("\[HL+", op_1) is not None:
                return 8
            else:
                return 4
        raise ValueError
            


    constraint_dict = {
                        # For the branches not taken
                        0: {
                            "bc": {
                                "set1": lambda *args: False, 
                                "clr1": lambda *args: True, 
                                "cmp": lambda x,y: x >= y
                                }, 
                            "bnz": {
                                "cmp": lambda x,y: x == y, 
                                },
                            "bz": {
                                "cmp": lambda x,y: x != y
                                }
                            }, 
                        # For branches taken - should be opposite 
                        1: {
                            "bc": {
                                "set1": lambda *args: True, 
                                "clr1": lambda *args: False, 
                                "cmp": lambda x,y: x < y
                                }, 
                            "bnz": {
                                "cmp": lambda x,y: x != y, 
                                },
                            "bz": {
                                "cmp": lambda x,y: x == y
                                }
                            }
                        }



    def translate_cond_br(self, constraint_ins, cond_br):
        '''
            Translates two instructions(e.g. cmp A, 0; bc ...) into a constraint
        '''
        _lambda = self.constraint_dict[cond_br.cond_true][cond_br.mnem][constraint_ins.mnem]
        # check if comparing to a constant
        for _i in range(len(constraint_ins.ops)):
            arg = constraint_ins.ops[_i]
            if re.search("#[0-9a-fA-F]+h", arg):
                _arg = int(arg.strip('#').strip('h'), 16) 
                if _i == 0:
                    return lambda x: _lambda(_arg, x)
                elif _i == 1:
                    return lambda x: _lambda(x, _arg)
        return _lambda
        

    success_insns = ["clr1"]
    error_insns = ["set1"]

    constraint_insns = ["cmp", "set1", "clr1"]
    mov_insns = ["mov", "movw"]



    def __init__(self):
        super(Rsas_78K0_Arch, self).__init__()
        self.instr_set = {"add": 4, "addc": 4, "cmp": 6, "mov": self.mov, "xch": 2, "divuw": 25, "ret": 6, "push": 4, "pop": 4, "dec": 2, "set1": self.bitwise_op, "clr1": self.bitwise_op, "call": 7, "movw": 8, "sub": 4, "inc": self.simple_arithmetic}


