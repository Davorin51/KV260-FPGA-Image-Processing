# Source provenance and scope

This repository is a new implementation written for Davorin Milicevic's open-source
portfolio request. The numerical conversion is a standard fixed-point weighted sum;
all implementation, tests, documentation and fixture generators here are newly authored.

The existing `Davorin51/Image-Processing-ZCU104` repository was inspected for directory
context only: root Adder/DSP/Sobel and Sobel/HLS, Sobel/Vivado. Its implementation files,
RTL, generated IP, notebooks, reports and binaries were not imported or copied. No
university/employer source or measurements are included or relicensed.

Public AMD documentation is linked for interface/board information, not copied into the
repository. AMD headers and tools are external prerequisites for optional HLS verification,
not bundled under this project's MIT license. Generated PNGs use deterministic synthetic
pixel patterns; no external photos or third-party artwork are included.

Commits represent actual incremental development without fabricated dates or historical
claims. GitHub Actions verifies host functionality, not an FPGA implementation.
