# Milestone 1 verification record

Authoring environment: Python 3.12, GNU C++, Linux. The captured tool-discovery record is
[environment-authoring.json](../benchmarks/environment-authoring.json). No AMD toolchain was
found, and a KV260 device was not accessed.

| Check actually executed | Result and scope |
| --- | --- |
| Strict portable C++ build | Passed C++14, warnings including conversion checks treated as errors |
| Portable arithmetic/frame testbench | Passed; all 16,777,216 RGB triples, frame diagnostics, invalid dimensions and seeded frames |
| pytest + Hypothesis | 30 passed; includes independent Python/C++ comparisons and a 1920×1080 random frame |
| Python host coverage | 97.74% in the authoring run; this is host coverage, not RTL coverage |
| Ruff lint + format | Passed |
| AddressSanitizer + UndefinedBehaviorSanitizer | Passed locally with leak detection disabled as described below |
| Python sdist and wheel | Successfully built locally and in all three CI jobs |
| GitHub Actions host matrix | Python 3.11, 3.12 and 3.13 passed, including the default sanitizer command |
| CPU example | Exact agreement for 8,192 pixels; zero differences, MSE 0 |
| AMD C simulation / synthesis / RTL co-simulation | Not run: required tools absent |
| FPGA board, DMA and actual timing/resource measurements | Not run |

## Sanitizer scope

The default `make sanitize` builds with AddressSanitizer and UndefinedBehaviorSanitizer. In
this supervised authoring environment, the initial default run failed inside LeakSanitizer
because it could not inspect `/proc` under process tracing. Running
`ASAN_OPTIONS=detect_leaks=0 make sanitize` passed ASan/UBSan. This does **not** verify leak
detection locally. The CI workflow runs the default command without that local workaround.
The first [GitHub Actions run](https://github.com/Davorin51/KV260-FPGA-Image-Processing/actions/runs/39130584013) subsequently passed on Python 3.11, 3.12 and 3.13, including the default sanitizer command, lint, tests, package build and demo generation.

## Evidence boundaries

The HLS testbench includes real AMD headers and calls the actual top function. It is staged
for vendor C simulation, not compiled by substituting mock AMD headers. The portable C++ tests
check the same arithmetic and framing core, but do not prove HLS elaboration, AXI signal
behavior, scheduling, timing closure, RTL equivalence or operation on a board.

A successful full-frame software comparison validates the documented integer transform and
binary layout. Hardware validation must separately address stream stalls, reset behavior,
backpressure, DMA length capacity, cache coherency and timeout/recovery.

Tests use synthetic fixtures generated from an explicit seed, not proprietary imagery.
The example report records its source binary and input/output checksums, timestamp, software
mode and explicit `not_run` hardware/tool stages. Regeneration may change timestamps and
binary hashes; the numerical contract and deterministic input pixels remain reproducible.
