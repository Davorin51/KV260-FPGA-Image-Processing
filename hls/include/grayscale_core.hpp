// SPDX-License-Identifier: MIT
#pragma once
#include <cstdint>

namespace kvimg {
constexpr std::uint32_t max_rows = 1080;
constexpr std::uint32_t max_cols = 1920;

inline std::uint8_t grayscale_pixel(std::uint8_t red, std::uint8_t green,
                                    std::uint8_t blue) {
#ifdef __SYNTHESIS__
#pragma HLS INLINE
#endif
    const std::uint32_t sum = 77u * red + 150u * green + 29u * blue + 128u;
    return static_cast<std::uint8_t>(sum >> 8u);
}

inline bool valid_dimensions(std::uint32_t rows, std::uint32_t cols) {
#ifdef __SYNTHESIS__
#pragma HLS INLINE
#endif
    return rows > 0 && cols > 0 && rows <= max_rows && cols <= max_cols;
}

// Portable value object, NOT an AMD AXI-interface type.
struct FrameWord {
    std::uint32_t data;
    std::uint8_t keep;
    std::uint8_t strb;
    bool last;
};

enum Status : std::uint32_t {
    ok = 0,
    invalid_dimensions = 1,
    bad_keep = 2,
    bad_strb = 4,
    bad_last = 8
};

// Transport provides FrameWord read() and void write(FrameWord).
// Synthesis uses an actual hls::stream adapter; host tests use a vector model.
template <typename Transport>
std::uint32_t grayscale_frame(Transport& transport, std::uint32_t rows,
                              std::uint32_t cols) {
    if (!valid_dimensions(rows, cols)) {
        return invalid_dimensions;
    }
    const std::uint32_t pixels = rows * cols;  // Safe after bounds checking.
    std::uint32_t status = ok;
    for (std::uint32_t index = 0; index < pixels; ++index) {
#ifdef __SYNTHESIS__
#pragma HLS PIPELINE II=1
#pragma HLS LOOP_TRIPCOUNT min=1 max=2073600
#endif
        const FrameWord incoming = transport.read();
        const bool end_of_frame = index == pixels - 1u;
        status |= incoming.keep == 0xFu ? ok : bad_keep;
        status |= incoming.strb == 0xFu ? ok : bad_strb;
        status |= incoming.last == end_of_frame ? ok : bad_last;
        const auto gray = grayscale_pixel(
            static_cast<std::uint8_t>(incoming.data & 0xFFu),
            static_cast<std::uint8_t>((incoming.data >> 8u) & 0xFFu),
            static_cast<std::uint8_t>((incoming.data >> 16u) & 0xFFu));
        const FrameWord outgoing{gray, 0xFu, 0xFu, end_of_frame};
        transport.write(outgoing);
    }
    return status;
}
}  // namespace kvimg
