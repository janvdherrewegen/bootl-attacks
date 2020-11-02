from ida_gdl import FlowChart
from ida_funcs import get_func
from ida_kernwin import gen_disasm_text, disasm_text_t, ask_str, ask_addr
from ida_lines import tag_remove, generate_disasm_line
from ida_ua import ua_mnem, print_operand
from ida_bytes import next_head, get_bytes, chunk_size
from ida_xref import get_first_cref_from, get_next_cref_from

import idc
import idaapi
from idautils import *

from arch import *
from cfg import cfg, CfgException
from extractor import Extractor

import cPickle


class IDA_Extractor(Extractor):

        
    def make_cfg(self, ea):
        '''Makes control flow graph of certain function'''
        f = get_func(ea)
        f_cfg = cfg(self.arch, f.startEA, f.endEA)
        bb_s = FlowChart(f)
        for ida_bb in bb_s:
            if ida_bb.startEA != ida_bb.endEA:
                bb = self.get_basic_blk(ida_bb)
                f_cfg.add_bb(bb)
                for xref in XrefsFrom(bb.end_ea()):
                    print "{:x} -> {:x}".format(xref.frm, xref.to)
                    # Check if basic block in the function graph already, if so take that reference
                    try:
                        bb_to = f_cfg.get_bb(xref.to)
                    except CfgException as e:
                        bb_to = self.get_bb(xref.to)
                    print bb_to
                    # Could be some data reference
                    if bb_to:
                        f_cfg.add_xref(bb, bb_to)
        return f_cfg


    def get_ticks(self, start_ea, end_ea):
        paths = self.get_paths(start_ea, end_ea)
        for p in paths:
            ticks = 0
            for bb in p:
                ticks += self.ticks(bb)
            print " -> ".join([hex(i.startEA) for i in p]), ": ", ticks

    def get_ins(self, addr):
        '''Gets instruction from address'''
        line = generate_disasm_line(addr)
        # get all operands
        n = 0
        ops = []
        op = tag_remove(print_operand(addr, n))
        while op:
            ops.append(op)
            n += 1
            op = tag_remove(print_operand(addr, n))
        ins = instruction(ua_mnem(addr), ops, addr) 
        ins.type = self.get_type(addr)
        # if instruction is a call instruction, reference the cfg
        if ins.type == instruction.TYPE_CALL:
            for ref in CodeRefsFrom(addr, 0):
                ins.calls = ref
        return ins

    def get_type(self, ins_addr):
        '''Get the instruction type of a certain addr'''
        if idaapi.is_call_insn(ins_addr):
            return instruction.TYPE_CALL
        xrefs = CodeRefsFrom(ins_addr, 0)
        is_jmp = 0
        # If there is a coderef, then we assume instruction is a jump instruction
        for xr in xrefs:
            is_jmp = 1
        if is_jmp:
            # Add a reference to the next instruction if the flow continues to it
            next_head = NextHead(ins_addr, 0xffffffff)
            if isFlow(GetFlags(next_head)):
                # refs holds the referenced address so you can use them later
                return instruction.TYPE_JMP_COND
            else:
                return instruction.TYPE_JMP_UNCOND   
        return instruction.TYPE_NORM


    def get_basic_blk(self, ida_bb):
        '''Creates a basic block from an ida basic block'''
        ret_bb = basic_blk()
        addr = ida_bb.startEA 
        while addr < ida_bb.endEA:
            ins = self.get_ins(addr)
            ret_bb.add_insn(ins)
            # IMPORTANT: append the calls from this function
            if ins.type == instruction.TYPE_CALL:
                self.cfgs_todo.append(ins.calls)
            addr = next_head(addr, ida_bb.endEA)
        return ret_bb

    def get_bb(self, ea):
        '''Gets basic_blk from address'''
        f = get_func(ea)
        if not f:
            return
        basic_blocks = FlowChart(f)
        for bb in basic_blocks:
            if bb.startEA <= ea and bb.endEA > ea:
                # we found the right basic block
                return self.get_basic_blk(bb)


# Python 2.7.13
# IDAPython v1.7.0 final 

if __name__ == "__main__":
    cc = IDA_Extractor(DummyArch())
    #f_cfg = cc.get_all_cfgs(0x892) # sanity_check_addr

    addr = ask_addr(0x1aa8,  "Please enter function address (in hex) to dump (Default: checksum_handler)")

    f_cfgs = cc.get_all_cfgs(addr)

    filename = ask_str("output.p", 4, "Please enter output file")

    cPickle.dump(f_cfgs, open(filename, 'wb'))


