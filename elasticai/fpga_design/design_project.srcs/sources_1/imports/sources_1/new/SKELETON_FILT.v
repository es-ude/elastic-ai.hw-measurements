`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 15.01.2025 15:54:41
// Design Name: 
// Module Name: SKELETON_FILT
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


module SKELETON_FILT#(
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

wire module_drdy, module_dvalid;
wire [BITWIDTH_IN-'d1:0] data_filt_in, data_filt_out;
assign RDY = module_drdy && module_dvalid;
assign DATA_OUT = {data_filt_out, {BITWIDTH_OFFSET{1'd0}}};
assign DATA_HEAD = {4'd5, 6'd1, 6'd1, BITWIDTH_IN[4:0], BITWIDTH_IN[4:0]};
assign data_filt_in = DATA_IN[BITWIDTH_OFFSET+:BITWIDTH_IN];


// --- DUT
Filter_IIR_1#(BITWIDTH_IN) FILT_STAGE(
    .CLK(CLK_SYS),
    .nRST(nRST),
    .EN(EN),
    .START_FLAG(TRGG_START_CALC),
    .DATA_IN(data_filt_in),
    .DATA_OUT(data_filt_out),
    .DATA_RDY(module_drdy),
    .DATA_VALID(module_dvalid)
);

endmodule
