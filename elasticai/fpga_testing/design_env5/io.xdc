# Device ENV5 Board with: xc7s15ftgb196-2, xc7s50ftgb196-1
# ************************ I/O Definition ************************************
# --- Clock
set_property -dict { PACKAGE_PIN H11 IOSTANDARD LVCMOS33 }  [get_ports { CLK_100MHz }];
create_clock -add -name clk_100 -period 10 -waveform {0 5}  [get_ports { CLK_100MHz }];

# --- SPI
set_property -dict { PACKAGE_PIN P12 IOSTANDARD LVCMOS33 }  [get_ports { SPI_CSN }];
set_property -dict { PACKAGE_PIN P11 IOSTANDARD LVCMOS33 }  [get_ports { SPI_MOSI }];
set_property -dict { PACKAGE_PIN M12 IOSTANDARD LVCMOS33 }  [get_ports { SPI_MISO }];
set_property -dict { PACKAGE_PIN N11 IOSTANDARD LVCMOS33 }  [get_ports { SPI_SCLK }];
set_property CLOCK_DEDICATED_ROUTE FALSE                    [get_nets SPI_SCLK]

# --- LEDs
set_property -dict { PACKAGE_PIN H12 IOSTANDARD LVCMOS33 }  [get_ports { LED[0] }];
set_property -dict { PACKAGE_PIN J12 IOSTANDARD LVCMOS33 }  [get_ports { LED[1] }];
set_property -dict { PACKAGE_PIN K12 IOSTANDARD LVCMOS33 }  [get_ports { LED[2] }];
set_property -dict { PACKAGE_PIN J11 IOSTANDARD LVCMOS33 }  [get_ports { LED[3] }];

# --- GPIO (FPGA <--> MCU)
#set_property -dict { PACKAGE_PIN M13 IOSTANDARD LVCMOS33 } [get_ports { M_GPIO[0] }];
#set_property -dict { PACKAGE_PIN P13 IOSTANDARD LVCMOS33 } [get_ports { M_GPIO[1] }];
set_property -dict { PACKAGE_PIN L12 IOSTANDARD LVCMOS33 }  [get_ports { FPGA_BUSY }];
set_property -dict { PACKAGE_PIN P10 IOSTANDARD LVCMOS33 }  [get_ports { RSTN }];

# --- GPIO (FPGA <--> Header)
#set_property -dict { PACKAGE_PIN A12 IOSTANDARD LVCMOS33 } [get_ports { F_GPIO[0] }];
#set_property -dict { PACKAGE_PIN A13 IOSTANDARD LVCMOS33 } [get_ports { F_GPIO[1] }];
#set_property -dict { PACKAGE_PIN B13 IOSTANDARD LVCMOS33 } [get_ports { F_GPIO[2] }];
#set_property -dict { PACKAGE_PIN C12 IOSTANDARD LVCMOS33 } [get_ports { F_GPIO[3] }];
#set_property -dict { PACKAGE_PIN B14 IOSTANDARD LVCMOS33 } [get_ports { F_GPIO[4] }];
#set_property -dict { PACKAGE_PIN D12 IOSTANDARD LVCMOS33 } [get_ports { F_GPIO[5] }];

# --- Configuration options, can be used for all designs
#set_property BITSTREAM.CONFIG.CONFIGRATE 50 [current_design]
#set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]
#set_property CONFIG_VOLTAGE 3.3 [current_design]
#set_property CFGBVS VCCO [current_design]
#set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]
