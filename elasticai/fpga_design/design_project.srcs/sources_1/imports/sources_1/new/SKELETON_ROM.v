`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 15.01.2025 15:54:21
// Design Name: 
// Module Name: SKELETON_ROM
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////

module SKELETON_ROM#(
    parameter BITWIDTH_IN = 5'd16,
    parameter BITWIDTH_SYS = 5'd16,
    parameter BITWIDTH_HEAD = 6'd32
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
assign DATA_HEAD = {4'd3, 6'd0, 6'd21, 5'd0, BITWIDTH_IN[4:0]};   
   

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
