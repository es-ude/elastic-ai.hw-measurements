//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
// 
// Create Date:     29.01.2025 06:24:33
// Copied on: 	    {$date_copy_created}
// Module Name:     SKELETON_RAM
// Target Devices:  FPGA
// Tool Versions:   1v0
// Description:     Skeleton for testing RAM structures on device
// Dependencies:    None
//
// State: 	        Not tested!
// Improvements:    None
// Parameters:      BITWIDTH_IN --> Bitwidth of input data
//                  BITWIDTH_SYS --> Bitwidth of data bus on device
//                  BITWIDTH_HEAD --> Bitwidth of metadata (skeleton properties)
//					ADR_WIDTH 		--> Bitwidth of adress range
//////////////////////////////////////////////////////////////////////////////////


module SKELETON_RAM#(
    parameter BITWIDTH_IN = 5'd12,
    parameter BITWIDTH_SYS = 5'd16,
    parameter BITWIDTH_HEAD = 6'd26,
	parameter BITWIDTH_ADR = 6'd6
)(
    input wire CLK_SYS,
    input wire RSTN,
    input wire EN,
    input wire TRGG_START_CALC,
    input wire RnW,
    input wire [BITWIDTH_ADR-'d1:0] ADR,
    input wire [BITWIDTH_SYS-'d1:0] DATA_IN,
    output wire [BITWIDTH_SYS-'d1:0] DATA_OUT,
    output wire [BITWIDTH_HEAD-'d1:0] DATA_HEAD,
    output wire RDY
);

localparam BITWIDTH_OFFSET = BITWIDTH_SYS - BITWIDTH_IN;
assign DATA_HEAD = {4'd4, BITWIDTH_ADR[5:0], BITWIDTH_ADR[5:0], BITWIDTH_IN[4:0], BITWIDTH_IN[4:0]};

wire [BITWIDTH_IN-'d1:0] ram_din, ram_dout;
assign ram_din = DATA_IN[(BITWIDTH_SYS-'d1)-:BITWIDTH_IN];
assign DATA_OUT = {ram_dout, {BITWIDTH_OFFSET{1'd0}}};

assign RDY = 1'd1;

// --- DUT INTEGRATION (JUST REPLACE HERE)
BRAM_SINGLE#(
    BITWIDTH_IN,
    2**BITWIDTH_ADR,
    ""
) DUT (
    .CLK_RAM(CLK_SYS),
    .EN(EN),
    .WE(RnW),
    .ADR(ADR),
    .DIN(ram_din),
    .DOUT(ram_dout)
);

endmodule
