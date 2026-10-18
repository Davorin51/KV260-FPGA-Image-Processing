# Explicit opt-in vendor execution; no guessed part or clock default.
set root [file normalize [file join [file dirname [info script]] ..]]
foreach key {HLS_PART HLS_CLOCK_NS HLS_STAGE} {
    if {![info exists ::env($key)] || $::env($key) eq ""} { error "Set $key explicitly" }
}
set stage $::env(HLS_STAGE)
if {$stage ni {csim synth cosim export}} { error "HLS_STAGE must be csim, synth, cosim or export" }
if {![string is double -strict $::env(HLS_CLOCK_NS)] || $::env(HLS_CLOCK_NS) <= 0} {
    error "HLS_CLOCK_NS must be a positive period in ns"
}
open_project -reset [file join $root .hls-build grayscale]
set_top grayscale_axis
add_files [file join $root hls grayscale grayscale_axis.cpp] -cflags "-std=c++14"
add_files -tb [file join $root tests test_grayscale_hls.cpp] -cflags "-std=c++14"
open_solution -reset solution -flow_target vivado
set_part $::env(HLS_PART)
create_clock -period $::env(HLS_CLOCK_NS) -name default
csim_design
if {$stage ne "csim"} { csynth_design }
if {$stage eq "cosim"} { cosim_design -rtl verilog }
if {$stage eq "export"} { export_design -format ip_catalog }
exit
