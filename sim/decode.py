"""
R-Type:  [opcode:4][rd:4][rs:4][rt:4]
I-Type:  [opcode:4][rd:4][rs:4][imm4:4]
Branch:  [opcode:4][cond:4][offset8:8]
M-Type:  [opcode:4][rd/rs:4][base:4][offset4:4]
J-Type:  [opcode:4][target12:12]
"""


def decode_r_type(instr):
    op_code = (instr >> 12) & 0xF
    rd = (instr >> 8) & 0xF
    rs = (instr >> 4) & 0xF
    rt = instr & 0xF
    return op_code, rd, rs, rt


def decode_i_type(instr):
    op_code = (instr >> 12) & 0xF
    rd = (instr >> 8) & 0xF
    rs = (instr >> 4) & 0xF
    imm4 = instr & 0xF
    return op_code, rd, rs, imm4


def decode_branch_type(instr):
    op_code = (instr >> 12) & 0xF
    cond = (instr >> 8) & 0xF
    offset = instr & 0xFF
    return op_code, cond, offset


def decode_m_type(instr):
    op_code = (instr >> 12) & 0xF
    rd_rs = (instr >> 8) & 0xF
    base = (instr >> 4) & 0xF
    offset = instr & 0xF
    return op_code, rd_rs, base, offset


def decode_j_type(instr):
    op_code = (instr >> 12) & 0xF
    target = instr & 0xFFF
    return op_code, target


def sign_extend_4bit(val):
    """Sign-extend 4-bit value to Python int"""
    if val & 0x8:
        return val | 0xFFFFFFF0
    return val


def sign_extend_8bit(val):
    """Sign-extend 8-bit value to Python int"""
    if val & 0x80:
        return val | 0xFFFFFF00
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
            0x7: self.exec_ext,
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
        self.pc += 4  # Move forward 1 instruction (4 nibbles)
        return instr

    def decode_and_execute(self, instr):
        op_code = (instr >> 12) & 0xF
        exec_func = self.dispatch.get(op_code)
        if exec_func:
            exec_func(instr)
        else:
            raise ValueError(f"Unknown Instruction: {op_code:X}")

    def write_reg(self, rd, value):
        if rd != 0:
            self.reg[rd] = value & 0xF

    def get_pair_value(self, base):
        """Get 8-bit value from register pair"""
        high = self.reg[base]
        low = self.reg[base + 1]
        return (high << 4) | low

    def exec_add(self, instr):
        _, rd, rs, rt = decode_r_type(instr)
        result = self.reg[rs] + self.reg[rt]
        self.flag_c = result > 0xF
        result &= 0xF
        self.flag_z = result == 0
        self.write_reg(rd, result)

    def exec_sub(self, instr):
        _, rd, rs, rt = decode_r_type(instr)
        result = self.reg[rs] - self.reg[rt]
        self.flag_c = result < 0
        result &= 0xF
        self.flag_z = result == 0
        self.write_reg(rd, result)

    def exec_and(self, instr):
        _, rd, rs, rt = decode_r_type(instr)
        result = self.reg[rs] & self.reg[rt]
        self.flag_c = False
        self.flag_z = result == 0
        self.write_reg(rd, result)

    def exec_or(self, instr):
        _, rd, rs, rt = decode_r_type(instr)
        result = self.reg[rs] | self.reg[rt]
        self.flag_c = False
        self.flag_z = result == 0
        self.write_reg(rd, result)

    def exec_xor(self, instr):
        _, rd, rs, rt = decode_r_type(instr)
        result = self.reg[rs] ^ self.reg[rt]
        self.flag_c = False
        self.flag_z = result == 0
        self.write_reg(rd, result)

    def exec_slt(self, instr):
        """Signed less-than comparison"""
        _, rd, rs, rt = decode_r_type(instr)
        rs_val = self.reg[rs]
        rt_val = self.reg[rt]
        # Convert to signed
        rs_signed = rs_val if rs_val < 8 else rs_val - 16
        rt_signed = rt_val if rt_val < 8 else rt_val - 16
        result = 1 if rs_signed < rt_signed else 0
        self.flag_c = False
        self.flag_z = result == 0
        self.write_reg(rd, result)

    def exec_shf(self, instr):
        """Shift left/right"""
        _, rd, rs, imm4 = decode_i_type(instr)
        rs_val = self.reg[rs]
        shift_dir = (imm4 >> 3) & 1
        shift_amt = imm4 & 0x7

        if shift_dir == 0:  # Left shift
            if shift_amt > 0:
                self.flag_c = bool((rs_val >> (4 - shift_amt)) & 1)
                result = (rs_val << shift_amt) & 0xF
            else:
                result = rs_val
                self.flag_c = False
        else:  # Right shift
            if shift_amt > 0:
                self.flag_c = bool((rs_val >> (shift_amt - 1)) & 1)
                result = rs_val >> shift_amt
            else:
                result = rs_val
                self.flag_c = False

        self.flag_z = result == 0
        self.write_reg(rd, result)

    def exec_ext(self, instr):
        """Extended operations: ADC, SBB, NEG, JR"""
        _, rd, rs, funct = decode_r_type(instr)

        if funct == 0x0:  # ADC
            result = self.reg[rd] + self.reg[rs] + (1 if self.flag_c else 0)
            self.flag_c = result > 0xF
            result &= 0xF
            self.flag_z = result == 0
            self.write_reg(rd, result)

        elif funct == 0x1:  # SBB
            result = self.reg[rd] - self.reg[rs] - (1 if self.flag_c else 0)
            self.flag_c = result < 0
            result &= 0xF
            self.flag_z = result == 0
            self.write_reg(rd, result)

        elif funct == 0x2:  # NEG
            result = (0 - self.reg[rs]) & 0xF
            self.flag_c = self.reg[rs] != 0
            self.flag_z = result == 0
            self.write_reg(rd, result)

        elif funct == 0x3:  # JR
            target = (self.reg[1] << 8) | (self.reg[2] << 4) | self.reg[3]
            self.pc = (target & 0xFFF) * 4  # Convert to nibble address

        else:
            raise ValueError(f"Unknown EXT function: {funct:X}")

    def exec_addi(self, instr):
        _, rd, rs, imm4 = decode_i_type(instr)
        imm_signed = sign_extend_4bit(imm4)
        result = self.reg[rs] + imm_signed
        self.flag_c = result > 0xF or result < 0
        result &= 0xF
        self.flag_z = result == 0
        self.write_reg(rd, result)

    def exec_andi(self, instr):
        _, rd, rs, imm4 = decode_i_type(instr)
        result = self.reg[rs] & imm4
        self.flag_c = False
        self.flag_z = result == 0
        self.write_reg(rd, result)

    def exec_ori(self, instr):
        _, rd, rs, imm4 = decode_i_type(instr)
        result = self.reg[rs] | imm4
        self.flag_c = False
        self.flag_z = result == 0
        self.write_reg(rd, result)

    def exec_slti(self, instr):
        _, rd, rs, imm4 = decode_i_type(instr)
        rs_val = self.reg[rs]
        rs_signed = rs_val if rs_val < 8 else rs_val - 16
        imm_signed = sign_extend_4bit(imm4)
        result = 1 if rs_signed < imm_signed else 0
        self.flag_c = False
        self.flag_z = result == 0
        self.write_reg(rd, result)

    def exec_lw(self, instr):
        _, rd, base, offset4 = decode_m_type(instr)
        offset_signed = sign_extend_4bit(offset4)
        addr = (self.get_pair_value(base) + offset_signed) & 0xFF
        value = self.memory[addr] & 0xF
        self.write_reg(rd, value)

    def exec_sw(self, instr):
        _, rs, base, offset4 = decode_m_type(instr)
        offset_signed = sign_extend_4bit(offset4)
        addr = (self.get_pair_value(base) + offset_signed) & 0xFF
        self.memory[addr] = self.reg[rs] & 0xF

    def exec_branch(self, instr):
        _, cond, offset8 = decode_branch_type(instr)
        offset_signed = sign_extend_8bit(offset8)

        taken = False
        if cond == 0x0:  # BEQ
            taken = self.flag_z
        elif cond == 0x1:  # BNE
            taken = not self.flag_z
        elif cond == 0x2:  # BCS
            taken = self.flag_c
        elif cond == 0x3:  # BCC
            taken = not self.flag_c

        if taken:
            self.pc = (self.pc + offset_signed * 4) & 0xFFF

    def exec_jump(self, instr):
        _, target12 = decode_j_type(instr)
        is_jal = (instr >> 11) & 1

        if is_jal:  # JAL
            # Save return address as instruction index
            ret_addr = self.pc // 4
            self.reg[1] = (ret_addr >> 8) & 0xF
            self.reg[2] = (ret_addr >> 4) & 0xF
            self.reg[3] = ret_addr & 0xF

            # Jump to 11-bit target (convert to nibble address)
            target = target12 & 0x7FF
            self.pc = target * 4  # ← FIX!
        else:  # J
            # Jump to 12-bit target (convert to nibble address)
            self.pc = target12 * 4  # ← FIX!

    def trace_state(self, cycle):
        sp = (self.reg[14] << 4) | self.reg[15]
        print(
            f"[{cycle:4d}] PC=0x{self.pc:03X} "
            f"r6={self.reg[6]:X} r7={self.reg[7]:X} r10={self.reg[10]:X} r11={self.reg[11]:X} "
            f"SP=0x{sp:02X}"
        )


"""
    def exec_jump(self, instr):
        _, target12 = decode_j_type(instr)
        is_jal = (instr >> 11) & 1

        if is_jal:  # JAL
            # Save return address (PC+4 in nibbles, convert to instruction number)
            ret_addr = self.pc // 4
            self.reg[1] = (ret_addr >> 8) & 0xF
            self.reg[2] = (ret_addr >> 4) & 0xF
            self.reg[3] = ret_addr & 0xF

            # Jump to 11-bit target (already in nibble units, don't multiply by 4!)
            target = target12 & 0x7FF  # Mask to 11 bits
            self.pc = target  # ← FIX: Don't multiply by 4!
        else:  # J
            # Jump to 12-bit target (already in nibble units)
            self.pc = target12  # ← FIX: Don't multiply by 4!
"""
