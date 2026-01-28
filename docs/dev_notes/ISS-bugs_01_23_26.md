# RISC-4 ISS Bug Log

This document chronicles all bugs discovered during ISS development (January 24, 2026).
Each bug includes the symptom, root cause, and fix for future reference.

---


### Bug #1: Missing Flag Initialization
**Symptom:** Flags had undefined behavior on first instruction
**Root Cause:** `__init__` didn't initialize `flag_c` and `flag_z`
**Fix:**
```python
def __init__(self):
    self.flag_c = False
    self.flag_z = False
```

### Bug #2: PC Increment Timing
**Symptom:** PC incremented before fetch, causing off-by-one errors
**Root Cause:** `fetch()` incremented PC, then `execute()` also modified it
**Fix:** Only increment PC in `fetch()`, let control flow instructions override

---

### Bug #3: Register r0 Not Hardwired to Zero
**Symptom:** Writing to r0 modified its value
**Root Cause:** `write_reg()` didn't check for r0
**Fix:**
```python
def write_reg(self, rd, value):
    if rd != 0:  # r0 is hardwired to zero
        self.reg[rd] = value & 0xF
```

### Bug #4: Branch Offset Not Sign-Extended
**Symptom:** Backward branches jumped to invalid addresses
**Root Cause:** 8-bit offset treated as unsigned
**Fix:**
```python
def sign_extend_8bit(value):
    if value & 0x80:  # Negative (bit 7 set)
        return value | 0xFFFFFF00
    return value
```

### Bug #5: Branch Offset Not Scaled to Nibbles
**Symptom:** Branches jumped to wrong addresses
**Root Cause:** Offset in bytes, but PC in nibbles
**Fix:**
```python
offset_nibbles = sign_extend_8bit(offset8) * 4
self.pc = (self.pc + offset_nibbles) & 0xFFF
```

### Bug #6: Flag Clearing in Logical Operations
**Symptom:** AND/OR/XOR didn't clear carry flag
**Root Cause:** Forgot to set `flag_c = False`
**Fix:**
```python
def exec_and(self, instr):
    # ... compute result ...
    self.flag_c = False  # Logical ops clear carry
    self.flag_z = (result == 0)
```

### Bug #7: SLT Didn't Handle Signed Comparison
**Symptom:** SLT gave wrong results for negative numbers
**Root Cause:** Used unsigned comparison
**Fix:**
```python
def to_signed(value):
    return value if value < 8 else value - 16

def exec_slt(self, instr):
    # ... decode ...
    rs_signed = to_signed(self.reg[rs])
    rt_signed = to_signed(self.reg[rt])
    result = 1 if rs_signed < rt_signed else 0
```

### Bug #8: Memory Address Calculation Wrong
**Symptom:** Load/store accessed wrong addresses
**Root Cause:** Forgot to combine register pair for base
**Fix:**
```python
def exec_load(self, instr):
    # ... decode ...
    base_addr = (self.reg[base] << 4) | self.reg[base + 1]
    offset_signed = sign_extend_4bit(offset4)
    addr = (base_addr + offset_signed) & 0xFF
```

### Bug #9: Store Used Wrong Register Field
**Symptom:** SW stored from rd instead of rs
**Root Cause:** Misread spec - SW uses bits [11:8] for source
**Fix:**
```python
def exec_store(self, instr):
    _, rs, base, offset4 = decode_m_type(instr)
    # rs is in bits [11:8] for SW, not rd
    # ... rest of implementation ...
```

### Bug #10: ADC/SBB Didn't Read Existing rd Value
**Symptom:** ADC/SBB computed wrong results
**Root Cause:** 2-operand destructive format not implemented
**Fix:**
```python
def exec_ext(self, instr):
    if funct == 0x0:  # ADC
        result = self.reg[rd] + self.reg[rs] + (1 if self.flag_c else 0)
        # ^^^^^^^^^^^ Must read rd first (destructive operation)
```

---

### Bug #11: Multi-Precision Test Used r0 as Destination
**Symptom:** 8-bit addition test failed - high nibble was always 0
**Root Cause:** Test code used r0 (hardwired zero) for result
**Fix:** Changed test to use r6 instead of r0

**Impact:** Not an ISS bug - just a test bug that revealed r0 behavior working correctly

### Bug #12: JAL Detection Checked Wrong Bit
**Symptom:** JAL not recognized, jumped like regular J
**Root Cause:** Checked bit 11 of decoded target instead of instruction
**Fix:**
```python
def exec_jump(self, instr):
    _, target12 = decode_j_type(instr)
    is_jal = (instr >> 11) & 1  # Check instruction bit 11, not target
```

**Impact:** Accidentally worked in some cases due to target having bit 11 set

### Bug #13: JAL/J Target Multiplied by 4
**Symptom:** JAL jumped to 4× the correct address
**Root Cause:** Target already in nibbles, but code multiplied by 4 again
**Fix:**
```python
def exec_jump(self, instr):
    if is_jal:
        target = target12 & 0x7FF  # Mask to 11 bits
        self.pc = target  # Already in nibbles, don't multiply!
    else:
        self.pc = target12  # Already in nibbles
```

---

## Summary Statistics

- **Total Bugs Found:** 13
- **Critical Bugs:** 5 (r0 hardwired, branch offset, JAL target, signed comparison, ADC/SBB)
- **Medium Bugs:** 6 (flag initialization, memory addressing, store register, JAL detection)
- **Minor Bugs:** 2 (PC timing, flag clearing)

## Lessons Learned

1. **Sign Extension is Hard:** Multiple bugs related to sign-extending 4-bit and 8-bit values
2. **Register r0 Special Case:** Easy to forget r0 is hardwired to zero
3. **Address Scaling:** Nibble vs byte vs instruction addressing caused confusion
4. **Destructive Operations:** 2-operand format (rd = rd OP rs) easy to implement wrong
5. **Bit Field Extraction:** Off-by-one errors in decode functions

## Testing Approach That Worked

- Start with simple 3-instruction test (ORI + ADD)
- Progress to multi-precision arithmetic (tests carry)
- Test branches (tests flags and PC calculation)
- Test memory (tests register pairs)
- Test function calls (tests JAL/JR and return address)

Each test revealed 1-3 bugs, allowing incremental fixes.

---

*This bug log serves as a reference for RTL development - many of these issues
will reappear in hardware form and need similar solutions.*
