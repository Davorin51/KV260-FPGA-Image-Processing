# KV260 setup: verified discovery before deployment

No AMD tools or connected board were found in the authoring environment. This is an
integration procedure, not a report that a block design/bitstream has been built.

1. On the actual development PC, source the installed AMD settings script. Do not infer
   the installed release from older projects or documentation examples.
2. Run `python scripts/inspect_environment.py --output benchmarks/environment-local.json`.
3. Run `vivado -mode batch -source scripts/inspect_vivado.tcl` to list actual tool version,
   matching K26 parts and available KV260/K26 board definitions. If empty, install board
   support using AMD's board-flow instructions. Do not substitute the ZCU104 board preset.
4. Select the actual KV260 starter-kit / K26 SOM plus carrier model offered by the installed
   version. Apply its PS DDR/peripheral preset; inspect the resulting device properties.
5. Supply `HLS_PART` and `HLS_CLOCK_NS` explicitly to the HLS run script. The clock is a
   requested constraint chosen for that design, not a measured or default KV260 frequency.

## Planned block-design integration

- Add the generated grayscale IP only after C simulation and synthesis pass.
- Configure AXI DMA for MM2S/S2MM, simple-mode frame packets, and 32-bit stream interfaces.
  These are PROPOSED design choices, not discovered settings in an existing design.
- Verify actual IP parameter support and the configured DMA buffer-length field. It must
  represent `4*rows*cols` bytes; the project's largest frame is 8,294,400 bytes. Do not
  assume the tool's default length field can hold a full frame. Start with a small frame.
- Connect DMA stream output -> grayscale input, grayscale output -> DMA stream input.
- Connect DMA memory masters through an appropriate interconnect to enabled PS DDR-access
  ports. Verify their actual width/address properties; AXI stream width does not prescribe
  the PS memory-port width. Keep the first system in one verified PL clock domain.
- Drive the AXI4-Lite slaves from an enabled PS master via a control interconnect.
- Use the actual clock and a correctly synchronized processor-system-reset network.
- Use Address Editor to assign addresses and export an XSA. Record its checksum, tool
  version, selected part, configured DMA parameters and clock constraint. Do not reuse
  addresses from the ZCU104 project or invent register offsets.
- Validate the block design; synthesize/implement and inspect timing before generating
  the bitstream. Export generated headers/metadata for the chosen Vitis software domain.

## Future board software sequence (driver not implemented)

Allocate two appropriately aligned, DMA-addressable buffers of exactly 4*N bytes. Under
Linux use a supported DMA allocation/driver path; virtual heap pointers are not physical
DMA addresses. Under bare metal use the BSP's actual drivers and cache-maintenance APIs.
Validate dimensions/length capacity, pack RGBX, synchronize source/destination caches as
required, arm S2MM first, program/start the IP, then start MM2S. Await all completions with
timeouts, inspect DMA errors and IP status, synchronize/invalidate the destination, and
compare with the independent Python reference. Do not assume HP/HPC transfers are coherent.

M1 includes no MMIO host driver, PYNQ overlay, ready-made bitstream or automated Vivado
block-design generator. Those require validation against the real installation and board.

## Official references

- [KV260 board flow, AMD UG1089](https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Vivado-Board-Flow)
- [K26 device family, AMD DS987](https://docs.amd.com/r/en-US/ds987-k26-som/Functional-Overview-and-Block-Diagram)
- [AXI DMA simple mode, AMD PG021](https://docs.amd.com/r/en-US/pg021_axi_dma/Direct-Register-Mode-Simple-DMA)
- [HLS AXI streams, AMD UG1399](https://docs.amd.com/r/en-US/ug1399-vitis-hls/How-AXI4-Stream-is-Implemented)
- [vitis-run command, AMD UG1702](https://docs.amd.com/r/en-US/ug1702-vitis-accelerated-reference/vitis-run-Command)
