// SPDX-License-Identifier: MIT
#include "grayscale_axis.hpp"
#include "../include/grayscale_core.hpp"

namespace {
struct AxisTransport {
    hls::stream<GrayAxisWord>& input;
    hls::stream<GrayAxisWord>& output;

    kvimg::FrameWord read() {
#pragma HLS INLINE
        const GrayAxisWord value = input.read();
        return {value.data.to_uint(), static_cast<std::uint8_t>(value.keep.to_uint()),
                static_cast<std::uint8_t>(value.strb.to_uint()), value.last != 0};
    }

    void write(const kvimg::FrameWord& value) {
#pragma HLS INLINE
        GrayAxisWord result{};
        result.data = value.data;
        result.keep = value.keep;
        result.strb = value.strb;
        result.last = value.last;
        output.write(result);
    }
};
}

void grayscale_axis(hls::stream<GrayAxisWord>& input,
                    hls::stream<GrayAxisWord>& output,
                    unsigned int rows, unsigned int cols,
                    unsigned int& status) {
#pragma HLS INTERFACE axis port=input
#pragma HLS INTERFACE axis port=output
#pragma HLS INTERFACE s_axilite port=rows bundle=control
#pragma HLS INTERFACE s_axilite port=cols bundle=control
#pragma HLS INTERFACE s_axilite port=status bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    AxisTransport transport{input, output};
    status = kvimg::grayscale_frame(transport, rows, cols);
}
