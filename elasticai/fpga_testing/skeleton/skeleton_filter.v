//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
// 
// Create Date:     15.01.2025 15:54:41
// Copied on: 	    {$date_copy_created}
// Module Name:     15.01.2025 15:54:41
// Target Devices:  FPGA
// Tool Versions:   1v0
// Description:     Skeleton for testing filter structures on device
// Dependencies:    None
//
// State: 	        Works! (System Test done: 16.01.2025)
// Improvements:    None
// Parameters:      BITWIDTH_IN 	--> Bitwidth of input data
//                  BITWIDTH_SYS 	--> Bitwidth of data bus on device
//                  BITWIDTH_HEAD	--> Bitwidth of metadata (skeleton properties)
//////////////////////////////////////////////////////////////////////////////////


module SKELETON_FILT#(
    parameter BITWIDTH_IN = 5'd16,
    parameter BITWIDTH_SYS = 5'd16,
    parameter BITWIDTH_HEAD = 6'd26
)(
    input wire CLK_SYS,
    input wire RSTN,
    input wire EN,
    input wire TRGG_START_CALC,
    input wire [BITWIDTH_SYS-'d1:0] DATA_IN,
    output wire [BITWIDTH_SYS-'d1:0] DATA_OUT,
    output wire [BITWIDTH_HEAD-'d1:0] DATA_HEAD,
    output wire RDY
);

localparam BITWIDTH_OFFSET = BITWIDTH_SYS - BITWIDTH_IN;
assign DATA_HEAD = {4'd5, 6'd1, 6'd1, BITWIDTH_IN[4:0], BITWIDTH_IN[4:0]};

wire module_drdy, module_dvalid;
wire [BITWIDTH_IN-'d1:0] data_filt_in, data_filt_out;
assign data_filt_in = DATA_IN[BITWIDTH_OFFSET+:BITWIDTH_IN];

assign RDY = module_drdy && module_dvalid;
assign DATA_OUT = {data_filt_out, {BITWIDTH_OFFSET{1'd0}}};

// --- DUT (JUST REPLACE HERE)
Filter_IIR_1#(BITWIDTH_IN) FILT_STAGE(
    .CLK(CLK_SYS),
    .RSTN(RSTN),
    .EN(EN),
    .START_FLAG(TRGG_START_CALC),
    .DATA_IN(data_filt_in),
    .DATA_OUT(data_filt_out),
    .DATA_RDY(module_drdy),
    .DATA_VALID(module_dvalid)
);

endmodule
