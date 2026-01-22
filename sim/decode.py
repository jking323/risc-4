'''
R-Type:  [opcode:4][rd:4][rs:4][rt:4]
I-Type:  [opcode:4][rd:4][rs:4][imm4:4]
Branch:  [opcode:4][cond:4][offset8:8]
M-Type:  [opcode:4][rd/rs:4][base:4][offset4:4]
J-Type:  [opcode:4][target12:12]
'''

def decode_r_type(instr):
    op_code = (instr << 12) & 0xF
    rd = (instr << 8) & 0xF
    rs = (instr << 4) & 0xF
    rt = (instr << 0) & 0xF
    return op_code, rd, rs, rt

def decode_i_type(instr):
    op_code = (instr << 12) & 0xF
    rd = (instr << 8) & 0xF
    rs = (instr << 4) & 0xF
    imm4 = (instr << 0) & 0xF
    return op_code, rd, rs, imm4

def decode_branch_type(instr):
    op_code = (instr << 12) & 0xF
    cond = (instr << 8) & 0xF
    offset = (instr << 0) & 0xFF
    return op_code, cond, offset

def decode_m_type(instr):
    op_code = (instr << 12) & 0xF
    rd_rs = (instr << 8) & 0xF
    base = (instr << 4) & 0xF
    offset = (instr << 0) & 0xF
    return op_code, rd_rs, base, offset

def decode_j_type(instr):
    op_code = (instr << 12) & 0xF
    target = (instr << 0) & 0xFFF
    return op_code, target

def sign_extend_4bit(val):
    if val & 0x8:
        return val | 0xFFFFFFF0
    return val

def sign_extend_8bit(val):
    if val & 0x80:
        return val | oxFFFFFF00
    return val

class RISC4:
    def __init__(self, mem_size=4096):
        self.reg = [0] * 16
        self.pc = 0
        self.flag_c = False
        self.flag_z = False
        self.memory = bytearray(mem_size)

        self.dispatch = {
                        0x0: self.exec_add,
                        0x1: self.exec_sub,
                        0x2: self.exec_and,
                        0x3: self.exec_or,
                        0x4: self.exec_xor,
                        0x5: self.exec_slt,
                        0x6: self.exec_shf,
                        0x7: self.exec_ext,  # ADC, SBB, NEG
                        0x8: self.exec_addi,
                        0x9: self.exec_andi,
                        0xA: self.exec_ori,
                        0xB: self.exec_slti,
                        0xC: self.exec_lw,
                        0xD: self.exec_sw,
                        0xE: self.exec_branch,
                        0xF: self.exec_jump,
                }

    def fetch(self):
        byte_addr = self.pc // 2
        instr = (self.memory[byte_addr] << 8) | self.memory[byte_addr + 1]
        self.pc += 4
        return instr

    def decode_and_execute(self, instr):
        op_code = (instr << 12) & 0xF
        exec_func = self.dispatch.get(op_code)
        if exec_func:
            exec_func(instr)
        else:
            raise ValueError(f"Unknown Instruction: {op_code:X}")

    def write_reg(self, rd, instr):
        if rd != 0:
            self.regs[rd] = value & 0xF

    def exec_add(self, instr):
        _, rd, rs, rt = decode_r_type(instr)
        result = rs + rt
        self.flag_c = (result > 0xF)
        result &= 0xF
        self.flag_z = (result == 0)
        self.write_reg(rd, result)
        pass

    def exec_sub(self, instr):
        _, rd, rs, rt = decode_r_type(instr)
        result = rs - rt
        self.flag_c = (result > 0xF)
        result &= 0xF
        self.flag_z = (result == 0)
        self.write_reg(rd, result)
        pass

    def exec_and(self, instr):
        _, rd, rs, rt = decode_r_type(instr)
        result = rs & rt
        self.flag_c = (result > 0xF)
        result &= 0xF
        self.flag_z = (result == 0)
        self.write_reg(rd, result)
        pass

    def


