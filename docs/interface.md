# Grayscale interface v1

## Numerical contract

Input is RGB, full unsigned range 0..255, without gamma correction or range rescaling.
The exact integer operation is:

`Y = floor((77*R + 150*G + 29*B + 128) / 256)`

Weights sum to 256, so every neutral `(g,g,g)` maps exactly to `g`. This is a specified
fixed-point luma approximation, not a claim of bit equivalence to every library's grayscale
conversion. The maximum rounded numerator is 65,408; uint32 arithmetic avoids overflow.

## Packet contract

| Signal/field | Definition |
| --- | --- |
| Input TDATA[7:0] | R |
| Input TDATA[15:8] | G |
| Input TDATA[23:16] | B |
| Input TDATA[31:24] | Ignored padding |
| Output TDATA[7:0] | Y |
| Output TDATA[31:8] | Zero padding |
| TKEEP / TSTRB | 0xF on every transfer, input and output |
| TLAST | Exactly the final pixel of the entire frame packet |
| TUSER / TID / TDEST | Not used by this interface |
| Raster order | Row-major, no stride or line padding |

Binary files contain little-endian uint32 words. Thus RGBX bytes are R,G,B,X and output
bytes are Y,0,0,0. Files contain exactly `4 * rows * cols` bytes, with no file header.
Images are separately stored as PNG. The opaque input padding byte is not alpha-blended.

This is a frame-packet AXI DMA contract, **not AXI4-Stream Video**. Video IP commonly uses
TLAST for end-of-line and TUSER for start-of-frame. Never connect those protocols directly
without a verified framing adapter or an appropriate video DMA architecture.

## Control and diagnostics

`rows`, `cols`, `status` and block control are grouped on the HLS `control` AXI4-Lite bundle.
The generated driver/header and IP metadata define register offsets; none are assumed here.
One invocation processes one frame. Auto-restart is not part of M1.

`status` is a bitmask produced at completion:

| Bit/value | Meaning |
| --- | --- |
| 0 / 1 | Invalid dimensions; consumes and produces no pixels |
| 1 / 2 | At least one input TKEEP differs from 0xF |
| 2 / 4 | At least one input TSTRB differs from 0xF |
| 3 / 8 | At least one input TLAST differs from the expected frame boundary |

Zero means no modeled input error. Invalid byte qualifiers mark the result invalid;
processing continues to the configured count for diagnostics, without promising meaningful
image values on invalid lanes. Output qualifiers and TLAST are always regenerated.

Dimensions must be validated BEFORE arming DMA. For a valid frame the accelerator consumes
exactly N inputs and produces N outputs. Missing beats stall a blocking stream; there is
no hardware timeout or packet resynchronization. An early TLAST can cause DMA to stop
feeding before N. Status then might never become available: the future host driver must
use bounded waits and reset/reinitialize DMA/IP on failure. Do not mistake diagnostics
for fault-tolerant stream recovery. A surplus beat belongs to the next invocation only
if that next invocation is explicitly scheduled and correctly framed.
