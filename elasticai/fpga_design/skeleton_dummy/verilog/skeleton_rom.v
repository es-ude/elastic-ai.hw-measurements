//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
// 
// Create Date:     15.01.2025 15:54:21
// Copied on: 	    {$date_copy_created}
// Module Name:     SKELETON_ROM
// Target Devices:  FPGA
// Tool Versions:   1v0
// Description:     Skeleton for testing ROM structures on device
// Dependencies:    None
//
// State: 	        Works! (System Test done: 16.01.2025)
// Improvements:    None
// Parameters:      BITWIDTH_IN --> Bitwidth of input data
//                  BITWIDTH_SYS --> Bitwidth of data bus on device
//                  BITWIDTH_HEAD --> Bitwidth of metadata (skeleton properties)
//					ADR_WIDTH 		--> Bitwidth of adress range
//////////////////////////////////////////////////////////////////////////////////


module SKELETON_ROM_{$device_id}#(
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
assign DATA_HEAD = {4'd3, 6'd0, ADR_WIDTH[5:0], 5'd0, BITWIDTH_IN[4:0]};   
   

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
