//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
// 
// Create Date:     13.01.2025 23:07:45
// Copied on: 	    {$date_copy_created}
// Module Name:     SKELETON_MATH
// Target Devices:  FPGA
// Tool Versions:   1v0
// Description:     Skeleton for testing math operations on device (in one system clock cycle)
// Dependencies:    None
//
// State: 	        Works! (System Test done: 16.01.2025)
// Improvements:    None
// Parameters:      BITWIDTH_IN 	--> Bitwidth of input data
//                  BITWIDTH_SYS 	--> Bitwidth of data bus on device
//                  BITWIDTH_ADR    --> Bitwidth of address range
//                  BITWIDTH_HEAD	--> Bitwidth of metadata (skeleton properties)
//////////////////////////////////////////////////////////////////////////////////


module SKELETON_MATH#(
    parameter BITWIDTH_IN = 5'd8,
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

localparam WAIT_CYC_MULT = 8'd4;
localparam BITWIDTH_OFFSET = BITWIDTH_SYS - BITWIDTH_IN;
localparam BITWIDTH_MULT_OUT = 2*BITWIDTH_IN;
localparam SIZE_INPUT = 2, SIZE_OUTPUT = 1;

assign DATA_HEAD = {4'd3, SIZE_INPUT[5:0], SIZE_OUTPUT[5:0], BITWIDTH_IN[4:0], BITWIDTH_MULT_OUT[4:0]};

// --- Control lines
reg run_test;
reg [$clog2(WAIT_CYC_MULT):0] cnt_mult_wait;
reg [BITWIDTH_IN-'d1:0] data_dut [SIZE_INPUT-'d1:0];
reg [BITWIDTH_IN-'d1:0] pipe_dut_in [SIZE_INPUT-'d1:0];
reg [2*BITWIDTH_IN-'d1:0] pipe_dut_out;

wire signed [2*BITWIDTH_IN-'d1:0] data_mul;
wire [BITWIDTH_IN*SIZE_INPUT-'d1:0] data0;

genvar k0;
for(k0 = 'd0; k0 < SIZE_INPUT; k0 = k0 + 'd1) begin
    assign data0[(k0*BITWIDTH_IN)+:BITWIDTH_IN] = data_dut[k0];
end
assign RDY = ~run_test;
assign DATA_OUT = {pipe_dut_out, {(BITWIDTH_SYS-BITWIDTH_MULT_OUT){1'd1}}};

integer i0;
always@(posedge CLK_SYS) begin
    if(~(RSTN && EN)) begin
        run_test <= 1'd0;
        cnt_mult_wait <= 'd0;
        pipe_dut_out <= 'd0;
        for(i0 = 'd0; i0 < SIZE_INPUT; i0 = i0 + 'd1) begin
            data_dut[i0] <= 'd0;
            pipe_dut_in[i0] <= 'd0;
        end
    end else begin
        // --- Loading data to internal RAM
        data_dut[ADR] <= (~RnW) ? DATA_IN[(BITWIDTH_SYS-'d1)-:BITWIDTH_IN] : data_dut[ADR];
        
        // --- Pipelining Multiplier Input (1-Delay Stage)
        if(run_test) begin
            run_test <= (cnt_mult_wait == WAIT_CYC_MULT) ? 1'd0 : run_test;
            cnt_mult_wait <= (cnt_mult_wait == WAIT_CYC_MULT) ? 'd0 : cnt_mult_wait + 'd1;
            
            pipe_dut_out <= data_mul;
            for(i0 = 'd0; i0 < SIZE_INPUT; i0 = i0 + 'd1) begin
                pipe_dut_in[i0] <= data_dut[i0];
            end
        end else begin
            run_test <= TRGG_START_CALC;
            cnt_mult_wait <= 'd0;
                   
            pipe_dut_out <= pipe_dut_out;
            for(i0 = 'd0; i0 < SIZE_INPUT; i0 = i0 + 'd1) begin
                pipe_dut_in[i0] <= pipe_dut_in[i0];
            end
        end
    end
end

// --- DUT (JUST REPLACE HERE)
MULT_LUT_SIGNED#(
    .BITWIDTH(BITWIDTH_IN)
) MULT (
    .A(pipe_dut_in[0]),
    .B(pipe_dut_in[1]),
    .Q(data_mul)
);

endmodule
