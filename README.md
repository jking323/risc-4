# RISC-4 ISA Specification

A 4-bit RISC architecture exploring the question: "What if the RISC
revolution happened in 1971 instead of 1981?"

## Quick Links

- [ISA Specification (PDF)](docs/isa-spec/releases/risc4-isa-v1.0.pdf)
- [Instruction Set Reference](docs/isa-spec/risc4-isa-spec.pdf#section.4)
- [Simulator & Tools](#tools)

## About

RISC-4 is a complete load/store RISC architecture with:
- 4-bit datapath
- 16 general-purpose registers
- 20 instructions (fixed 16-bit encoding)
- 5-stage pipeline design
- Compare-to-zero branches

This ISA is implemented in silicon as part of the
[4004-recreation project](https://github.com/jkin323/intel-4004-recreation).

## Getting Started

### Run the Simulator
```bash
python3 sim/risc4_sim.py examples/fibonacci.r4
```

### Assemble Code
```bash
python3 asm/risc4_asm.py examples/hello.s -o hello.r4
```

## Citation

If you use RISC-4 in academic work, please cite:
```bibtex
@misc{king2026risc4,
  author = {Jeremy, Jeremy},
  title = {RISC-4: A 4-bit RISC Architecture},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/jking323/risc-4}},
  note = {Version 1.0}
}
```

## Implementations

- **Reference (this repo):** ISA simulator in Python
- **Silicon:** [SKY130 tapeout](https://github.com/jking323/intel-4004-recreation)
- **FPGA:** *(community contributions welcome)*

## License

- **Documentation & Specification:** CC-BY-4.0
- **Code (simulator, assembler):** MIT

See LICENSE files for details.

## Related Work

- Intel 4004 (1971) - Historical inspiration
- Berkeley RISC-I (1981) - RISC principles
- RISC-V (2010) - Modern RISC ISA
