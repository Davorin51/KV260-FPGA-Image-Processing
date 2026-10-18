// SPDX-License-Identifier: MIT
#pragma once
#include <ap_axi_sdata.h>
#include <hls_stream.h>

using GrayAxisWord = ap_axiu<32, 0, 0, 0>;
void grayscale_axis(hls::stream<GrayAxisWord>& input,
                    hls::stream<GrayAxisWord>& output,
                    unsigned int rows, unsigned int cols,
                    unsigned int& status);
