# Development milestones

## M1 - Grayscale and a reproducible verification foundation (in progress)

- Original fixed-point grayscale core and independent Python reference.
- Portable C++ frame model and binary CPU utility.
- AXI4-Stream HLS wrapper, explicit framing and a vendor-header testbench.
- Seeded fixtures, numerical comparison, local tests, CI and honest verification record.
- User-machine tool/part/board inspection scripts; no fabricated board settings.

## M2 - Validate the interface with the actual AMD installation and KV260

- Run vendor-header C simulation, then synthesis and RTL co-simulation.
- Inspect generated AXI4-Lite register map and measured scheduling/resources.
- Select actual installed K26 board files and configure PS DDR/clock/reset via board flow.
- Integrate DMA and execute a small frame on the board with bounded waits and cache handling.
- Preserve raw logs, XSA metadata, configurations and input/output hashes.

## M3 - Sobel 3x3

- Add a separately reusable grayscale Sobel stage with two line buffers and a 3x3 window.
- Specify border policy and integer magnitude/saturation before implementation.
- Verify tiny images, borders, impulses, random frames and back-to-back frames.

## M4 - Neighborhood filter library

Gaussian 3x3/5x5, sharpening and configurable convolution. Define coefficients, accumulator
widths, normalization/rounding and saturation explicitly. Threshold follows as a point stage.
Optional erosion/dilation come after the convolution/window infrastructure is verified.

## M5 - Optimization and evidence

Compare a real baseline and optimized variants using actual HLS and implementation reports.
Explore pipelining, unrolling, partitioning, BRAM and DSP trade-offs only as relevant to each
kernel. Add robust report extraction, CPU timing studies and provenance-backed plots.
Hardware FPS requires actual timed board runs; synthesis estimates are labeled separately.

## M6 - Host product polish

Hardware transport/driver, on-board comparison, richer HTML/PDF review reports and additional
image formats. No placeholder drivers, guessed MMIO maps or invented measurements.
