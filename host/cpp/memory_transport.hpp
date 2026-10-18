// SPDX-License-Identifier: MIT
#pragma once
#include "../../hls/include/grayscale_core.hpp"
#include <stdexcept>
#include <vector>

// SOFTWARE ONLY. Underflow throws here; real hardware would block.
struct MemoryTransport {
    std::vector<kvimg::FrameWord> input;
    std::vector<kvimg::FrameWord> output;
    std::size_t position = 0;
    kvimg::FrameWord read() {
        if (position >= input.size()) {
            throw std::runtime_error("Software frame model: insufficient input words");
        }
        return input[position++];
    }
    void write(const kvimg::FrameWord& value) { output.push_back(value); }
};
