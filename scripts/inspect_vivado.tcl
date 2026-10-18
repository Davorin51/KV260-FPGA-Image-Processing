# Read-only discovery. Does not create a project, choose clocks or assign addresses.
puts "VIVADO_VERSION [version -short]"
foreach part [get_parts -quiet *xck26*] { puts "INSTALLED_PART $part" }
foreach board [get_board_parts -quiet *] {
    if {[regexp -nocase {kv260|k26} $board]} { puts "INSTALLED_BOARD $board" }
}
exit
