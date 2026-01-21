//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
// 
// Create Date:     12.11.2024 12:21:17
// Copied on: 	    {$date_copy_created}
// Module Name:     SKELETON_MATH_SLOW
// Target Devices:  FPGA
// Tool Versions:   1v0
// Description:     Skeleton for testing math operations on device (in two UART transmission cycle)
// Dependencies:    None
//
// State: 	        Works! (System Test done: 16.01.2025)
// Improvements:    None
// Parameters:      BITWIDTH_IN 	--> Bitwidth of input data
//                  BITWIDTH_SYS 	--> Bitwidth of data bus on device
//                  BITWIDTH_HEAD	--> Bitwidth of metadata (skeleton properties)
//					ADR_WIDTH 		--> Bitwidth of adress range
//////////////////////////////////////////////////////////////////////////////////


module SKELETON_MULT_SLOW_{$device_id}#(
    parameter BITWIDTH_IN = 5'd8,
    parameter SIZE_INPUT = 5'd2,
    parameter BITWIDTH_ADR = 6'd6,
    parameter BITWIDTH_SYS = 5'd16,
    parameter BITWIDTH_HEAD = 6'd32
)(
    input wire CLK_SYS,
    input wire nRST,
    input wire EN,
    input wire TRGG_START_CALC,
    input wire RnW,
    input wire [BITWIDTH_ADR-'d1:0] ADR,
    input wire [BITWIDTH_SYS-'d1:0] DATA_IN,
    output wire [BITWIDTH_SYS-'d1:0] DATA_OUT,
    output wire [BITWIDTH_HEAD-'d7:0] DATA_HEAD,
    output wire RDY
);

localparam BITWIDTH_OFFSET = BITWIDTH_SYS - BITWIDTH_IN;
localparam BITWIDTH_MULT_OUT = 2*BITWIDTH_IN;
assign DATA_HEAD = {4'd1, {1'd0, SIZE_INPUT[4:0]}, 6'd1, BITWIDTH_IN[4:0], BITWIDTH_MULT_OUT[4:0]};

// --- Control lines
reg flag_start_dly;
reg [BITWIDTH_IN-'d1:0] data_dut [SIZE_INPUT-'d1:0];
reg [BITWIDTH_IN-'d1:0] pipe_dut_in [SIZE_INPUT-'d1:0];
reg [2*BITWIDTH_IN-'d1:0] pipe_dut_out;

wire signed [2*BITWIDTH_IN-'d1:0] data_mul;
assign RDY = ~TRGG_START_CALC && EN;
assign DATA_OUT = {pipe_dut_out, {(BITWIDTH_SYS-BITWIDTH_MULT_OUT){1'd0}}};

integer i0;
always@(posedge CLK_SYS) begin
    if(~(nRST && EN)) begin
        flag_start_dly <= 1'd0;
        pipe_dut_out <= 'd0;
        for(i0 = 'd0; i0 < SIZE_INPUT; i0 = i0 + 'd1) begin
            data_dut[i0] <= 'd0;
            pipe_dut_in[i0] <= 'd0;
        end
    end else begin
        flag_start_dly <= TRGG_START_CALC && EN;
        // --- Loading data to internal RAM
        data_dut[ADR] <= (~RnW) ? DATA_IN[(BITWIDTH_SYS-'d1)-:BITWIDTH_IN] : data_dut[ADR];
        // --- Pipelining Multiplier Input (1-Delay Stage)
        if(flag_start_dly && ~TRGG_START_CALC) begin
            pipe_dut_out <= data_mul;
            for(i0 = 'd0; i0 < SIZE_INPUT; i0 = i0 + 'd1) begin
                pipe_dut_in[i0] <= data_dut[i0];
            end
        end else begin
            pipe_dut_out <= pipe_dut_out;
            for(i0 = 'd0; i0 < SIZE_INPUT; i0 = i0 + 'd1) begin
                pipe_dut_in[i0] <= pipe_dut_in[i0];
            end
        end
    end
end


// --- DUT (JUST REPLACE HERE)
LUT_MULT_SIGNED#(BITWIDTH_IN) MULT_UNIT(
    .A(pipe_dut_in[0]),
    .B(pipe_dut_in[1]),
    .Q(data_mul)
);


endmodule
