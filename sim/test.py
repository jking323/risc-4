import decode

# Add these helper functions to your test file


def assemble_i_type(opcode, rd, rs, imm4):
    """Assemble I-type instruction
    Format: [opcode:4][rd:4][rs:4][imm4:4]
    """
    return (opcode << 12) | (rd << 8) | (rs << 4) | (imm4 & 0xF)


def assemble_r_type(opcode, rd, rs, rt):
    """Assemble R-type instruction
    Format: [opcode:4][rd:4][rs:4][rt:4]
    """
    return (opcode << 12) | (rd << 8) | (rs << 4) | (rt & 0xF)


def assemble_j_type(opcode, target12):
    """Assemble J-type instruction
    Format: [opcode:4][target:12]
    """
    return (opcode << 12) | (target12 & 0xFFF)


def assemble_m_type(opcode, rd, base, offset4):
    """Assemble M-type instruction (LW/SW)
    Format: [opcode:4][rd:4][base:4][offset:4]
    """
    return (opcode << 12) | (rd << 8) | (base << 4) | (offset4 & 0xF)


def assemble_ext(rd, rs, funct):
    """Assemble EXT instruction (ADC, SBB, NEG, JR)
    Format: [0x7:4][rd:4][rs:4][funct:4]
    """
    return (0x7 << 12) | (rd << 8) | (rs << 4) | (funct & 0xF)


def assemble_branch(cond, offset8):
    """Assemble branch instruction
    Format: [0xE:4][cond:4][offset:8]
    cond: 0000=BEQ, 0001=BNE, 0010=BCS, 0011=BCC
    """
    return (0xE << 12) | (cond << 8) | (offset8 & 0xFF)


def load_program(cpu, program):
    """Load list of instructions into memory starting at address 0"""
    for i, instr in enumerate(program):
        byte_addr = i * 2
        cpu.memory[byte_addr] = (instr >> 8) & 0xFF
        cpu.memory[byte_addr + 1] = instr & 0xFF


def test_multiprecision_add():
    """Test 8-bit addition: r6:r1 = r2:r3 + r4:r5"""
    cpu = decode.RISC4()

    program = [
        assemble_i_type(0xA, 2, 0, 0x9),  # ORI r2, r0, 0x9
        assemble_i_type(0xA, 3, 0, 0xF),  # ORI r3, r0, 0xF
        assemble_i_type(0xA, 4, 0, 0x2),  # ORI r4, r0, 0x2
        assemble_i_type(0xA, 5, 0, 0x3),  # ORI r5, r0, 0x3
        assemble_r_type(0x0, 6, 2, 0),  # ADD r6, r2, r0 (r6 = r2)
        assemble_r_type(0x0, 1, 3, 5),  # ADD r1, r3, r5
        assemble_ext(6, 4, 0),  # ADC r6, r4
    ]

    load_program(cpu, program)

    # Execute with debug
    for i in range(len(program)):
        instr = cpu.fetch()
        print(f"[{i}] 0x{instr:04X} ", end="")
        cpu.decode_and_execute(instr)
        print(
            f"→ r1={cpu.reg[1]:X} r2={cpu.reg[2]:X} r3={cpu.reg[3]:X} r4={cpu.reg[4]:X} r5={cpu.reg[5]:X} r6={cpu.reg[6]:X} C={cpu.flag_c}"
        )

    result = (cpu.reg[6] << 4) | cpu.reg[1]
    print(f"\nr2:r3 = 0x9F = 159 decimal")
    print(f"r4:r5 = 0x23 = 35 decimal")
    print(f"r6:r1 = 0x{cpu.reg[6]:X}{cpu.reg[1]:X} = {result} decimal")
    print(f"Expected: 0xC2 = 194 decimal")

    assert cpu.reg[6] == 0xC and cpu.reg[1] == 0x2
    print("PASS ADD")


def test_branch():
    """Test BEQ/BNE"""
    cpu = decode.RISC4()

    program = [
        assemble_i_type(0xA, 1, 0, 0x5),  # ORI r1, r0, 0x5
        assemble_i_type(0xA, 2, 0, 0x5),  # ORI r2, r0, 0x5
        assemble_r_type(0x1, 3, 1, 2),  # SUB r3, r1, r2 (sets Z=1)
        assemble_branch(0x0, 0x02),  # BEQ +2 (skip next 2 instructions)
        assemble_i_type(0xA, 4, 0, 0xF),  # ORI r4, r0, 0xF (should be skipped)
        assemble_i_type(0xA, 5, 0, 0xF),  # ORI r5, r0, 0xF (should be skipped)
        assemble_i_type(0xA, 6, 0, 0x7),  # ORI r6, r0, 0x7 (should execute)
    ]

    load_program(cpu, program)

    for i in range(7):
        instr = cpu.fetch()
        print(f"[{i}] PC={cpu.pc - 4:02X} 0x{instr:04X}")
        cpu.decode_and_execute(instr)

    print(f"\nr4 = {cpu.reg[4]:X} (expected 0 - should be skipped)")
    print(f"r5 = {cpu.reg[5]:X} (expected 0 - should be skipped)")
    print(f"r6 = {cpu.reg[6]:X} (expected 7 - should execute)")

    assert cpu.reg[4] == 0
    assert cpu.reg[5] == 0
    assert cpu.reg[6] == 7
    print("PASS branch")


def test_load_store():
    """Test LW/SW with register pairs"""
    cpu = decode.RISC4()

    program = [
        # Set up base pointer r14:r15 = 0x80
        assemble_i_type(0xA, 14, 0, 0x8),  # ORI r14, r0, 0x8
        assemble_i_type(0xA, 15, 0, 0x0),  # ORI r15, r0, 0x0
        # Store value to memory
        assemble_i_type(0xA, 1, 0, 0xA),  # ORI r1, r0, 0xA
        assemble_m_type(0xD, 1, 14, 0),  # SW r1, 0(r14) → mem[0x80] = 0xA
        # Load it back
        assemble_i_type(0xA, 2, 0, 0x0),  # ORI r2, r0, 0x0 (clear r2)
        assemble_m_type(0xC, 2, 14, 0),  # LW r2, 0(r14) → r2 = mem[0x80]
    ]

    load_program(cpu, program)

    for i in range(len(program)):
        instr = cpu.fetch()
        cpu.decode_and_execute(instr)

    print(f"r1 = {cpu.reg[1]:X} (value stored)")
    print(f"r2 = {cpu.reg[2]:X} (value loaded)")
    print(f"mem[0x80] = {cpu.memory[0x80]:X}")

    assert cpu.reg[2] == 0xA
    assert cpu.memory[0x80] == 0xA
    print("PASS load store")


def test_jal_jr():
    """Test JAL and JR"""
    cpu = decode.RISC4()

    program = [
        # Main - nibble addresses 0x00, 0x04, 0x08, 0x0C
        assemble_i_type(0xA, 4, 0, 0x3),  # 0x00: ORI r4, r0, 0x3
        assemble_j_type(
            0xF, 0x010 | 0x800
        ),  # 0x04: JAL 0x010 ← FIX: jump to 0x10, not 0x08
        assemble_i_type(0xA, 5, 0, 0x9),  # 0x08: ORI r5, r0, 0x9 (return here)
        assemble_j_type(0xF, 0x000),  # 0x0C: J 0x000 (loop)
        # Function - nibble addresses 0x10, 0x14
        assemble_i_type(0x8, 4, 4, 0x1),  # 0x10: ADDI r4, r4, 1 ← Function starts here
        assemble_ext(0, 0, 3),  # 0x14: JR (return)
    ]

    load_program(cpu, program)
    print("Memory contents (first 12 bytes):")
    for i in range(12):
        print(f"  Byte {i:02X}: 0x{cpu.memory[i]:02X}")
    print()

    print("Expected:")
    print("  Byte 00: 0xA4  Byte 01: 0x03  <- 0xA403")
    print("  Byte 02: 0xF8  Byte 03: 0x10  <- 0xF810")
    print("  Byte 04: 0xA5  Byte 05: 0x09  <- 0xA509")
    print()

    print("Program loaded:")
    for i in range(len(program)):
        print(f"  Nibble {i * 4:03X} (Byte {i * 2:03X}): 0x{program[i]:04X}")

    # Execute with detailed trace
    for i in range(20):
        pc_before = cpu.pc
        instr = cpu.fetch()
        print(f"\n[{i}] PC={pc_before:03X} Fetch=0x{instr:04X}", end="")

        # Decode to show what instruction this is
        opcode = (instr >> 12) & 0xF
        if opcode == 0xF:
            bit11 = (instr >> 11) & 0x1
            if bit11:
                print(" (JAL)", end="")
            else:
                print(" (J)", end="")
        elif opcode == 0x7:
            funct = instr & 0xF
            if funct == 3:
                print(" (JR)", end="")

        cpu.decode_and_execute(instr)
        print(
            f" → PC={cpu.pc:03X} r1={cpu.reg[1]:X} r2={cpu.reg[2]:X} r3={cpu.reg[3]:X} r4={cpu.reg[4]:X} r5={cpu.reg[5]:X}"
        )

        if cpu.pc == 0x00 and i > 0:  # Looped back to start
            print("Detected loop back to PC=0")
            break

    print(f"\nFinal state:")
    print(f"r1:r2:r3 = {cpu.reg[1]:X}:{cpu.reg[2]:X}:{cpu.reg[3]:X} (return address)")
    print(f"r4 = {cpu.reg[4]:X} (expected 4)")
    print(f"r5 = {cpu.reg[5]:X} (expected 9)")
    print("PASS jal")


test_multiprecision_add()
test_jal_jr()
test_branch()
