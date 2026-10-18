// SPDX-License-Identifier: MIT
// Compile ONLY with the actual AMD headers/tools, not portable-header substitutes.
#include "../hls/grayscale/grayscale_axis.hpp"
#include <iostream>

static bool run_frame(hls::stream<GrayAxisWord>& input,
                      hls::stream<GrayAxisWord>& output,
                      unsigned rows, unsigned cols, bool corrupt_last) {
    const unsigned count = rows * cols;
    for (unsigned i = 0; i < count; ++i) {
        GrayAxisWord word{};
        word.data = ((i * 79u) & 255u) | (((i * 47u) & 255u) << 8u) |
                    (((i * 17u) & 255u) << 16u);
        word.keep = 15;
        word.strb = 15;
        word.last = corrupt_last ? false : i + 1 == count;
        input.write(word);
    }
    unsigned status = 999;
    grayscale_axis(input, output, rows, cols, status);
    if (status != (corrupt_last ? 8u : 0u)) { return false; }
    for (unsigned i = 0; i < count; ++i) {
        if (output.empty()) { return false; }
        const auto word = output.read();
        const unsigned expected = (77u*((i*79u)&255u) + 150u*((i*47u)&255u) + 29u*((i*17u)&255u) +128u)/256u;
        if (word.data != expected || word.keep != 15 || word.strb != 15 ||
            (word.last != 0) != (i + 1 == count)) { return false; }
    }
    return input.empty() && output.empty();
}

int main() {
    hls::stream<GrayAxisWord> input;
    hls::stream<GrayAxisWord> output;
    if (!run_frame(input, output, 1, 1, false) ||
        !run_frame(input, output, 13, 17, false) ||
        !run_frame(input, output, 7, 5, true)) {
        std::cerr << "FAIL: AMD-header testbench\n";
        return 1;
    }
    unsigned status = 999;
    grayscale_axis(input, output, 0, 10, status);
    if (status != 1 || !input.empty() || !output.empty()) { return 1; }
    std::cout << "PASS: AMD-header grayscale testbench\n";
    return 0;
}
