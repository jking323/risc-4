import decode

# ============================================================
# Assembly Helper Functions (from your reference)
# ============================================================


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


def load_data_nibbles(cpu, start_addr, data):
    """Load nibble data into memory at nibble addresses"""
    for i, nibble in enumerate(data):
        cpu.memory[start_addr + i] = nibble & 0xF


# ============================================================
# Bubble Sort Test
# ============================================================


def test_bubble_sort():
    """Test recursive bubble sort implementation"""
    cpu = decode.RISC4()

    print("=" * 60)
    print("RISC-4 BUBBLE SORT TEST")
    print("=" * 60)

    # Build the complete program
    # Addresses are in NIBBLES (each instruction = 4 nibbles = 2 bytes)
    program = []

    # ========== MAIN ==========
    program.append(assemble_i_type(0xA, 14, 0, 0xF))  # [0] ORI r14, r0, 0xF
    program.append(assemble_i_type(0xA, 15, 0, 0xF))  # [1] ORI r15, r0, 0xF
    program.append(assemble_i_type(0xA, 4, 0, 0x4))  # [2] ORI r4, r0, 0x4
    program.append(assemble_i_type(0xA, 5, 0, 0x0))  # [3] ORI r5, r0, 0x0
    program.append(assemble_i_type(0xA, 6, 0, 0x5))  # [4] ORI r6, r0, 0x5
    program.append(assemble_j_type(0xF, 0x08 | 0x800))  # [5] JAL 0x08
    program.append(assemble_j_type(0xF, 0x06))  # [6] J 0x018 (self)
    program.append(assemble_i_type(0x0, 0, 0, 0))  # [7] NOP

    # ========== BUBBLE_SORT @ index 8 ==========
    prologue_start = len(program)  # Should be 8
    program.append(assemble_i_type(0xB, 7, 15, 5))  # [8]  SLTI r7, r15, 5
    program.append(assemble_branch(0x0, 0x01))  # [9]  BEQ +1 (skip ADDI r14)
    program.append(assemble_i_type(0x8, 14, 14, 0xF))  # [10] ADDI r14, r14, -1
    program.append(assemble_i_type(0x8, 15, 15, 0xB))  # [11] ADDI r15, r15, -5
    program.append(assemble_m_type(0xD, 1, 14, 0))  # [12] SW r1, 0(r14)
    program.append(assemble_m_type(0xD, 2, 14, 1))  # [13] SW r2, 1(r14)
    program.append(assemble_m_type(0xD, 3, 14, 2))  # [14] SW r3, 2(r14)
    program.append(assemble_m_type(0xD, 10, 14, 3))  # [15] SW r10, 3(r14)
    program.append(assemble_m_type(0xD, 11, 14, 4))  # [16] SW r11, 4(r14)

    # Base case check
    base_check_idx = len(program)  # Should be 17
    program.append(assemble_i_type(0xB, 7, 6, 2))  # [17] SLTI r7, r6, 2

    # Placeholder for BNE - we'll calculate offset after knowing base_case index
    bne_basecase_idx = len(program)  # Should be 18
    program.append(0x0000)  # PLACEHOLDER

    program.append(assemble_i_type(0xA, 10, 0, 0))  # [19] ORI r10, r0, 0
    program.append(assemble_i_type(0x8, 11, 6, 0xF))  # [20] ADDI r11, r6, -1

    # Loop start
    loop_start_idx = len(program)  # Should be 21
    program.append(assemble_r_type(0x1, 7, 10, 11))  # [21] SUB r7, r10, r11

    # Placeholder for BCC to loop_done
    bcc_loopdone_idx = len(program)  # Should be 22
    program.append(0x0000)  # PLACEHOLDER

    program.append(assemble_r_type(0x0, 8, 5, 0))  # [23] ADD r8, r5, r0
    program.append(assemble_r_type(0x0, 9, 4, 0))  # [24] ADD r9, r4, r0
    program.append(assemble_r_type(0x0, 8, 5, 10))  # [25] ADD r8, r5, r10
    program.append(assemble_branch(0x3, 0x01))  # [26] BCC +1
    program.append(assemble_i_type(0x8, 9, 9, 1))  # [27] ADDI r9, r9, 1
    program.append(assemble_m_type(0xC, 2, 8, 0))  # [28] LW r2, 0(r8)
    program.append(assemble_m_type(0xC, 3, 8, 1))  # [29] LW r3, 1(r8)
    program.append(assemble_r_type(0x1, 7, 2, 3))  # [30] SUB r7, r2, r3

    # Placeholder for BCS to no_swap
    bcs_noswap_idx = len(program)  # Should be 31
    program.append(0x0000)  # PLACEHOLDER

    # Placeholder for BEQ to no_swap
    beq_noswap_idx = len(program)  # Should be 32
    program.append(0x0000)  # PLACEHOLDER

    program.append(assemble_m_type(0xD, 3, 8, 0))  # [33] SW r3, 0(r8)
    program.append(assemble_m_type(0xD, 2, 8, 1))  # [34] SW r2, 1(r8)

    # no_swap
    no_swap_idx = len(program)  # Should be 35
    program.append(assemble_i_type(0x8, 10, 10, 1))  # [35] ADDI r10, r10, 1
    program.append(assemble_j_type(0xF, loop_start_idx))  # [36] J loop

    # loop_done
    loop_done_idx = len(program)  # Should be 37
    program.append(assemble_i_type(0x8, 6, 6, 0xF))  # [37] ADDI r6, r6, -1
    program.append(assemble_j_type(0xF, prologue_start | 0x800))  # [38] JAL bubble_sort

    # base_case (epilogue)
    base_case_idx = len(program)  # Should be 39
    program.append(assemble_m_type(0xC, 1, 14, 0))  # [39] LW r1, 0(r14)
    program.append(assemble_m_type(0xC, 2, 14, 1))  # [40] LW r2, 1(r14)
    program.append(assemble_m_type(0xC, 3, 14, 2))  # [41] LW r3, 2(r14)
    program.append(assemble_m_type(0xC, 10, 14, 3))  # [42] LW r10, 3(r14)
    program.append(assemble_m_type(0xC, 11, 14, 4))  # [43] LW r11, 4(r14)
    program.append(assemble_i_type(0x8, 15, 15, 5))  # [44] ADDI r15, r15, 5
    program.append(assemble_branch(0x3, 0x01))  # [45] BCC +1
    program.append(assemble_i_type(0x8, 14, 14, 1))  # [46] ADDI r14, r14, 1
    program.append(assemble_ext(0, 0, 3))  # [47] JR r1

    # Now calculate and fill in branch offsets
    # BNE at index 18 to base_case at index 39
    offset_bne = base_case_idx - (bne_basecase_idx + 1)
    program[bne_basecase_idx] = assemble_branch(0x1, offset_bne)

    # BCC at index 22 to loop_done at index 37
    offset_bcc = loop_done_idx - (bcc_loopdone_idx + 1)
    program[bcc_loopdone_idx] = assemble_branch(0x3, offset_bcc)

    # BCS at index 31 to no_swap at index 35
    offset_bcs = no_swap_idx - (bcs_noswap_idx + 1)
    program[bcs_noswap_idx] = assemble_branch(0x2, offset_bcs)

    # BEQ at index 32 to no_swap at index 35
    offset_beq = no_swap_idx - (beq_noswap_idx + 1)
    program[beq_noswap_idx] = assemble_branch(0x0, offset_beq)

    print(f"Branch offset calculations:")
    print(
        f"  BNE base_case: index {bne_basecase_idx} → {base_case_idx}, offset = {offset_bne}"
    )
    print(
        f"  BCC loop_done: index {bcc_loopdone_idx} → {loop_done_idx}, offset = {offset_bcc}"
    )
    print(
        f"  BCS no_swap:   index {bcs_noswap_idx} → {no_swap_idx}, offset = {offset_bcs}"
    )
    print(
        f"  BEQ no_swap:   index {beq_noswap_idx} → {no_swap_idx}, offset = {offset_beq}"
    )

    # Load program
    load_program(cpu, program)

    # Load test data
    test_array = [0x7, 0x2, 0x9, 0x1, 0x5]
    load_data_nibbles(cpu, 0x40, test_array)

    print("\nInitial array at 0x40:")
    for i in range(5):
        print(f"  mem[0x{0x40 + i:02X}] = {cpu.memory[0x40 + i]}")

    # Execute
    max_cycles = 5000
    cycle = 0

    print("\nExecuting bubble sort...")
    print("(showing first 100 cycles)\n")

    while cycle < max_cycles:
        cpu.trace_state(cycle)
        pc_before = cpu.pc

        if cpu.pc == 0x18 and cycle > 0:
            print(f"\n[Cycle {cycle}] Reached done loop at PC=0x{cpu.pc:03X}")
            break

        instr = cpu.fetch()

        if cycle < 100:
            print(f"[{cycle:4d}] PC=0x{pc_before:03X} Instr=0x{instr:04X}", end="")

        cpu.decode_and_execute(instr)

        if cycle < 100:
            print(
                f" → r6={cpu.reg[6]:X} r10={cpu.reg[10]:X} SP={cpu.reg[14]:X}{cpu.reg[15]:X} mem[40-44]={[cpu.memory[0x40 + i] for i in range(5)]}"
            )

        cycle += 1

    if cycle >= max_cycles:
        print(f"\n!!! Hit cycle limit !!!")

    print(f"\nTotal cycles: {cycle}")
    print("\nFinal array at 0x40:")
    for i in range(5):
        print(f"  mem[0x{0x40 + i:02X}] = {cpu.memory[0x40 + i]}")

    expected = [0x1, 0x2, 0x5, 0x7, 0x9]
    actual = [cpu.memory[0x40 + i] for i in range(5)]

    print("\nVerification:")
    print(f"  Expected: {expected}")
    print(f"  Actual:   {actual}")

    if actual == expected:
        print("\n✓ PASS - Array is correctly sorted!")
    else:
        print("\n✗ FAIL - Array is not sorted correctly")

    assert actual == expected

    return cpu


if __name__ == "__main__":
    test_bubble_sort()
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
