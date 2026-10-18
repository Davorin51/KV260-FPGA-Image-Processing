// SPDX-License-Identifier: MIT
#include "memory_transport.hpp"
#include <array>
#include <fstream>
#include <iostream>
#include <limits>
#include <string>

static std::uint32_t dimension(const std::string& value) {
    if (value.empty() || value.find_first_not_of("0123456789") != std::string::npos) {
        throw std::runtime_error("Dimensions must be positive decimal integers");
    }
    const auto number = std::stoull(value);
    if (number > std::numeric_limits<std::uint32_t>::max()) {
        throw std::runtime_error("Dimension exceeds uint32");
    }
    return static_cast<std::uint32_t>(number);
}

int main(int argc, char** argv) {
    try {
        if (argc != 5) {
            throw std::runtime_error("Usage: grayscale_cpu input.rgbx output.gray32 rows cols");
        }
        const auto rows = dimension(argv[3]);
        const auto cols = dimension(argv[4]);
        if (!kvimg::valid_dimensions(rows, cols)) {
            throw std::runtime_error("Dimensions must be 1..1080 rows and 1..1920 columns");
        }
        if (std::string(argv[1]) == std::string(argv[2])) {
            throw std::runtime_error("Input and output paths must differ");
        }
        const std::uint32_t count = rows * cols;
        std::ifstream source(argv[1], std::ios::binary);
        if (!source) { throw std::runtime_error("Cannot open input file"); }
        MemoryTransport transport;
        transport.input.reserve(count);
        transport.output.reserve(count);
        for (std::uint32_t i = 0; i < count; ++i) {
            std::array<unsigned char, 4> bytes{};
            source.read(reinterpret_cast<char*>(bytes.data()), 4);
            if (source.gcount() != 4) { throw std::runtime_error("Input is shorter than the configured frame"); }
            const std::uint32_t word = static_cast<std::uint32_t>(bytes[0]) |
                (static_cast<std::uint32_t>(bytes[1]) << 8u) |
                (static_cast<std::uint32_t>(bytes[2]) << 16u) |
                (static_cast<std::uint32_t>(bytes[3]) << 24u);
            transport.input.push_back({word, 0xFu, 0xFu, i == count - 1u});
        }
        char extra = 0;
        if (source.get(extra)) { throw std::runtime_error("Input contains extra bytes after the configured frame"); }
        if (kvimg::grayscale_frame(transport, rows, cols) != kvimg::ok) {
            throw std::runtime_error("Unexpected software frame diagnostic");
        }
        std::ofstream destination(argv[2], std::ios::binary | std::ios::trunc);
        if (!destination) { throw std::runtime_error("Cannot open output file"); }
        for (const auto& word : transport.output) {
            const std::array<unsigned char, 4> bytes{static_cast<unsigned char>(word.data), 0, 0, 0};
            destination.write(reinterpret_cast<const char*>(bytes.data()), 4);
        }
        destination.close();
        if (!destination) { throw std::runtime_error("Failed to write complete output"); }
        std::cout << "CPU model processed " << count << " pixels; no FPGA execution\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
