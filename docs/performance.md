# Performance methodology

No FPGA performance or resource measurements have been collected. The grayscale loop requests
II=1 with an HLS pragma; that request is not evidence of achieved initiation interval or timing.
No target clock has been selected without an installed part/platform inspection.

## Evidence to collect in the next milestone

1. Record git commit, tool version, exact selected part/board, source checksum and all constraints.
2. Preserve the raw HLS synthesis report and logs: achieved II, latency bounds, estimated clock,
   LUT, FF, BRAM and DSP. Label HLS estimates separately from implemented resource/timing results.
3. Preserve Vivado implementation utilization and timing summaries. A positive slack result must
   cite the actual constraint, route status and tool configuration.
4. Compare identical fixed fixtures against the independent Python reference. Record input/output
   hashes and numerical differences before measuring speed.
5. On the real board, time repeated completed frame transfers with warm-up, bounded waits and
   error checking. Report whether timings include copies, cache handling and both DMA directions.
6. Distinguish kernel-only time from end-to-end latency. Hardware FPS must come from measured
   completed frames and elapsed time; do not derive a hardware claim from HLS clock/II estimates.

Use at least one simple baseline and one justified optimization with unchanged numerical
semantics. Keep frame size, pixel format, transport overhead and constraints constant for fair
comparisons. Future report parsers and plots must preserve raw source report paths and never
fill missing fields with fabricated zeros. They are not part of milestone 1.

The checked-in example measures numerical agreement only. Its elapsed execution, if any, must
not be presented as FPGA throughput. Full-HD software correctness testing does not establish
full-HD board operation, timing closure or a camera/video integration.
