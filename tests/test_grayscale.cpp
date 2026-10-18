// SPDX-License-Identifier: MIT
#include "../hls/include/grayscale_core.hpp"
#include "../host/cpp/memory_transport.hpp"
#include <cstdint>
#include <iostream>
#include <random>
#include <stdexcept>
#include <utility>

static void require(bool condition, const char* message) {
    if (!condition) { throw std::runtime_error(message); }
}

static void scalar_exhaustive() {
    std::uint64_t checked = 0;
    for (unsigned int red = 0; red < 256; ++red) {
        for (unsigned int green = 0; green < 256; ++green) {
            for (unsigned int blue = 0; blue < 256; ++blue) {
                // Separately expressed integer oracle; no shared helper call.
                const auto expected = (red * 77u + green * 150u + blue * 29u + 128u) / 256u;
                require(kvimg::grayscale_pixel(static_cast<std::uint8_t>(red),
                          static_cast<std::uint8_t>(green), static_cast<std::uint8_t>(blue)) == expected,
                        "Exhaustive RGB mismatch");
                ++checked;
            }
        }
    }
    require(checked == 16777216u, "Incomplete exhaustive sweep");
    require(kvimg::grayscale_pixel(255, 0, 0) == 77, "Red oracle");
    require(kvimg::grayscale_pixel(0, 255, 0) == 149, "Green oracle");
    require(kvimg::grayscale_pixel(0, 0, 255) == 29, "Blue oracle");
    std::cout << "Exhaustive scalar RGB checks: " << checked << '\n';
}

static void framing() {
    MemoryTransport io;
    io.input = {{0xAA0000FFu, 15, 15, false}, {0x0000FF00u, 15, 15, true},
                {0x00FF0000u, 15, 15, true}};
    require(kvimg::grayscale_frame(io, 1, 2) == 0, "First frame status");
    require(io.position == 2 && io.output.size() == 2, "First frame boundary");
    require(io.output[0].data == 77 && io.output[1].data == 149, "Pixel output");
    require(!io.output[0].last && io.output[1].last, "Frame TLAST");
    require(kvimg::grayscale_frame(io, 1, 1) == 0, "Second frame status");
    require(io.output[2].data == 29 && io.output[2].last, "Second frame/replay");
    MemoryTransport bad;
    bad.input = {{0xFFFFFFu, 1, 0, true}, {0, 15, 15, false}};
    require(kvimg::grayscale_frame(bad, 1, 2) == (kvimg::bad_keep | kvimg::bad_strb | kvimg::bad_last), "Diagnostic bitmask");
    require(!bad.output[0].last && bad.output[1].last, "Regenerated TLAST");
    for (const auto& word : bad.output) {
        require(word.keep == 15 && word.strb == 15 && word.data <= 255, "Output format");
    }
    MemoryTransport empty;
    for (const auto& dims : {std::pair<unsigned, unsigned>{0, 1}, {1, 0}, {1081, 1}, {1, 1921}, {0xFFFFFFFFu, 0xFFFFFFFFu}}) {
        require(kvimg::grayscale_frame(empty, dims.first, dims.second) == kvimg::invalid_dimensions, "Dimension guard");
        require(empty.position == 0 && empty.output.empty(), "Invalid frame consumed data");
    }
    bool underflow = false;
    try { kvimg::grayscale_frame(empty, 1, 1); }
    catch (const std::runtime_error&) { underflow = true; }
    require(underflow, "Software-model underflow not caught");
    require(kvimg::valid_dimensions(1080, 1920), "Project maximum guard");
}

static void random_frames() {
    std::mt19937 generator(51);
    for (unsigned trial = 0; trial < 80; ++trial) {
        const unsigned rows = 1u + static_cast<unsigned>(generator() % 41u);
        const unsigned cols = 1u + static_cast<unsigned>(generator() % 53u);
        MemoryTransport io;
        for (unsigned i = 0; i < rows * cols; ++i) {
            io.input.push_back({static_cast<std::uint32_t>(generator()), 15, 15, i + 1u == rows * cols});
        }
        require(kvimg::grayscale_frame(io, rows, cols) == 0, "Random status");
        require(io.output.size() == io.input.size(), "Random output length");
        for (std::size_t i = 0; i < io.output.size(); ++i) {
            const auto word = io.input[i].data;
            const auto expected = (77u*(word&255u) + 150u*((word>>8u)&255u) + 29u*((word>>16u)&255u) +128u)/256u;
            require(io.output[i].data == expected, "Random frame numerical mismatch");
            require(io.output[i].last == (i + 1 == io.output.size()), "Random TLAST");
        }
    }
}

int main() {
    try {
        scalar_exhaustive();
        framing();
        random_frames();
        std::cout << "PASS: portable C++ arithmetic/frame tests (not AMD C simulation)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what() << '\n';
        return 1;
    }
}
