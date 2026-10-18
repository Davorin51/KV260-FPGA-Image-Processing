# KV260 FPGA Image Processing

Original, incremental classical image-processing work targeting the AMD Kria KV260.
No neural networks, inference or AI model evaluation are part of this project.

## First milestone

Implement and numerically verify an RGB-to-grayscale point-processing core, a portable
stream/frame model, a separate Vitis HLS AXI4-Stream wrapper and independent Python
reference tools. Later neighborhood filters remain future work.

The authoring environment currently has GCC and Python but no detected AMD tools.
No HLS simulation, synthesis, RTL co-simulation, implementation or board execution has
been performed. An II=1 pragma is an optimization request, not a measured result.

See [architecture](docs/architecture.md), [stream contract](docs/interface.md),
[KV260 setup](docs/kv260_setup.md), [roadmap](ROADMAP.md) and [provenance](docs/provenance.md).
