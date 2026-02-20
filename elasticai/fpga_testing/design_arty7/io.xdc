# Device Arty7 DevBoard with: xc7a35ticsg324-1L, XC7A100TCSG324-1
# ************************ I/O Definition ************************************
# CLOCK AND RESET
set_property -dict {PACKAGE_PIN E3  IOSTANDARD LVCMOS33} [get_ports CLK_100MHz]
set_property -dict {PACKAGE_PIN C2  IOSTANDARD LVCMOS33} [get_ports RSTN]

create_clock -period 10.000 -name sys_clk -waveform {0.000 5.000} -add [get_ports CLK_100MHz]
set_property PULLUP true [get_ports RSTN]
set_false_path -from [get_ports RSTN] -to [all_outputs]

# --- I/O
set_property -dict {PACKAGE_PIN T10 IOSTANDARD LVCMOS33} [get_ports {LED[3]}]
set_property -dict {PACKAGE_PIN T9  IOSTANDARD LVCMOS33} [get_ports {LED[2]}]
set_property -dict {PACKAGE_PIN J5  IOSTANDARD LVCMOS33} [get_ports {LED[1]}]
set_property -dict {PACKAGE_PIN H5  IOSTANDARD LVCMOS33} [get_ports {LED[0]}]

# --- UART
set_property -dict {PACKAGE_PIN D10 IOSTANDARD LVCMOS33} [get_ports {UART_TX}]
set_property -dict {PACKAGE_PIN A9  IOSTANDARD LVCMOS33} [get_ports {UART_RX}]
