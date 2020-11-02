import re
import constraint
from path import path
from arch import instruction

from lambda_source import get_short_lambda_source


class constraint_solver:

    def __init__(self, path, symb_vars, constraints = []):
        '''
            path: all instructions along the path to calculate the constraints
            symb_vars: array of tuples for symbolic vars: (var_name, values)
        '''
        self.path_constraints = constraint.Problem()
        self.symb_vars = []
        for _tup in symb_vars:
            self.path_constraints.addVariable(_tup[0], _tup[1])
            self.symb_vars.append(_tup[0])
        for _tup in constraints:
            self.path_constraints.addConstraint(_tup[0], _tup[1])
        self.path = path
        self._pretty_constraints = []

    def propagate_var(self, var, idx):
        '''
            Backwards propagation to see where variable is set
        '''
        var_propagation = [] 
        curr_var = var
        for _j in range(idx, -1, -1):
            ins = self.path.insns[_j]
            # if the variable is propagated 
            if ins.mnem in self.path.arch.mov_insns and curr_var in ins.ops[0]: 
                var_propagation.append(ins.ops[1])
                curr_var = ins.ops[1]
                if curr_var in self.symb_vars:
                    return var_propagation
        return var_propagation


    def handle_cond_branch(self, br_ins, idx):
        # Traverse the path backwards to check where constraint originates from
        for _j in range(idx, -1, -1):
            ins = self.path.insns[_j]
            if ins.mnem in self.path.arch.constraint_insns:
                constr = self.path.arch.translate_cond_br(ins, br_ins)
                # Get constraint operands
                if constr: 
                    symb_vars = [None, None]
                    for _i in range(len(ins.ops)):
                        arg = ins.ops[_i]
                        # if arg is a immediate operand
                        if re.search("#[0-9a-fA-F]+h", arg):
                            pass
                        elif arg in self.symb_vars:
                            symb_vars[_i] = arg
                        else:
                            prop = self.propagate_var(arg, idx)
                            # if symbolic var propagated
                            intersect = set(prop).intersection(set(self.symb_vars))
                            if intersect:
                                symb_vars[_i] = intersect.pop()
                    self._pretty_constraints.append((get_short_lambda_source(constr),symb_vars[0], symb_vars[1]))
                    if symb_vars[0] and symb_vars[1]:
                        self.path_constraints.addConstraint(constr, symb_vars)
                    elif symb_vars[0]:
                        self.path_constraints.addConstraint(constr, [symb_vars[0]])
                    elif symb_vars[1]:
                        self.path_constraints.addConstraint(constr, [symb_vars[1]])
                    else:
                        self.path_constraints.addConstraint(constr)
                return
                

    def get_constraints(self):
        for _i in range(len(self.path.insns)):
            curr_insn = self.path.insns[_i]
            if curr_insn.type == instruction.TYPE_JMP_COND:
                self.handle_cond_branch(curr_insn, _i)
        return self.path_constraints.getSolution()

