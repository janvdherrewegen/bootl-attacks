# This script extracts a set of control flow graphs for a given function
#@author Jan Van den Herrewegen
#@category _NEW_
#@keybinding 
#@menupath 
#@toolbar 

# Set this to the absolute path of the repo
SCRIPT_DIR = "/home/.../bootl-attacks"

import sys
sys.path.append(SCRIPT_DIR)

# Ghidra imports
from ghidra.program.model.block import SimpleBlockModel, BasicBlockModel, CodeBlockIterator
from ghidra.program.model.listing import Function, ListingStub
from ghidra.program.model.address import Address
from ghidra.program.model.symbol import RefType 
# Own imports
from v850e1_instruction_set import *
from extractor import Extractor
from clk_count import cfg

class Ghidra_Extractor(Extractor):

    def __init__(self, arch):
        super(Ghidra_Extractor, self).__init__(arch)


    def convert_basic_blk(self, cb):
        '''Converts a ghidra CodeBlock to a basic_blk object'''
        ret_bb = basic_blk(self.convert_addr(cb.getFirstStartAddress()))
        ret_bb.fall_through = self.convert_addr(cb.getMaxAddress().add(1))
        for addr in cb.getAddresses(cb.getFirstStartAddress(), 1):
            ins = getInstructionAt(addr)
            if not ins:
                continue
            ins_conv = self.convert_ins(ins)
            flow_t = ins.getFlowType()
            if flow_t.isCall():
                ins_conv.type = instruction.TYPE_CALL
                for call in ins.getDefaultFlows():
                    ret_bb.calls.add(self.get_cfg(self.convert_addr(call)))
            elif flow_t.isJump() and flow_t.isConditional():
                ins_conv.type = instruction.TYPE_JMP_COND
            ret_bb.add_insn(ins_conv) 
        
        return ret_bb

    def convert_ins(self, ins):
        '''Converts a ghidra instruction to a instruction object'''
        ops = []
        for i in range(ins.getNumOperands()):
             ops.append(ins.getDefaultOperandRepresentation(i))
        return instruction(ins.getMnemonicString(), ops, ins.getAddress().getUnsignedOffset(), ins.getBytes())

    def convert_addr(self, addr):
        '''Converts a ghidra address to an unsigned long'''
        return int(addr.getUnsignedOffset())

    def get_cfg(self, addr):
        '''Makes a function control flow graph for a certain addr (in long!)'''
        f_cfg = super(Ghidra_Extractor, self).get_cfg(addr)
        if f_cfg:
            return f_cfg
        addr = currentProgram.getAddressFactory().getAddress(hex(addr))
        f = getFunctionContaining(addr)
        if f:
            asv = f.getBody()
            end_ea = self.convert_addr(asv.getLastRange().getMaxAddress())
        else:
            end_ea = 0x0
        sbm = BasicBlockModel(currentProgram)
        curr_block = sbm.getCodeBlockAt(addr, monitor)
        if not curr_block:
            raise CfgException("Codeblock at {:x} not found".format(addr))
        f_cfg = cfg(self.arch, self.convert_addr(curr_block.getFirstStartAddress()))
        if end_ea:
            f_cfg.end_addr = end_ea + 1
        code_block_stack = set()
        code_block_stack.add(curr_block)
        while code_block_stack: 
            blk = code_block_stack.pop()
            bb = self.convert_basic_blk(blk)
            # If basic block is already in the cfg, just skip to the next one
            if f_cfg.add_bb(bb):
                continue
            # add xrefs to other bbs
            xref_it = blk.getDestinations(monitor)
            while xref_it.hasNext():
                xref = xref_it.next()
                ft = xref.getFlowType()
                from_addr = xref.getReferent()
                # only add references from the last instruction to the cfg
                if not ft.isCall():
                    bb_to = self.convert_basic_blk(xref.getDestinationBlock())
                    f_cfg.add_xref(bb, bb_to)
                    code_block_stack.add(xref.getDestinationBlock())
                # otherwise we are calling a function
                elif ft.isCall():
                    self.cfgs_todo.append(self.convert_addr(xref.getDestinationAddress())) 
        self.funcs_done.add(f_cfg)
        return f_cfg


