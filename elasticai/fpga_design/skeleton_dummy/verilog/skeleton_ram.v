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


module SKELETON_RAM_{$device_id}#(
    parameter BITWIDTH_IN = 5'd16,
    parameter BITWIDTH_SYS = 5'd16,
    parameter BITWIDTH_HEAD = 6'd32,
	parameter ADR_WIDTH = 6'd21
)(
    input wire CLK_SYS,
    input wire nRST,
    input wire EN,
    input wire TRGG_START_CALC,
    input wire [BITWIDTH_SYS-'d1:0] DATA_IN,
    output wire [BITWIDTH_SYS-'d1:0] DATA_OUT,
    output wire [BITWIDTH_HEAD-'d7:0] DATA_HEAD,
    output wire RDY
);
    
localparam BITWIDTH_OFFSET = BITWIDTH_SYS - BITWIDTH_IN;

wire [BITWIDTH_IN-'d1:0] dout_rom; 
assign DATA_OUT = {dout_rom, {BITWIDTH_OFFSET{1'd0}}};
assign DATA_HEAD = {4'd3, ADR_WIDTH[5:0], ADR_WIDTH[5:0], BITWIDTH_IN[4:0], BITWIDTH_IN[4:0]};   
   

// --- DUT INTEGRATION
LUT_WVF_GEN0 DUT(
    .CLK_SYS(CLK_SYS),
    .nRST(nRST),
    .EN(EN),
    .TRGG_CNT_FLAG(TRGG_START_CALC),
    .LUT_VALUE(dout_rom),
    .LUT_END(RDY)
);


endmodule
