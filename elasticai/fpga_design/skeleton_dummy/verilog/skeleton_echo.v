//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
// 
// Create Date:     20.12.2024 12:54:02
// Copied on: 	    {$date_copy_created}
// Module Name:     SKELETON_ECHO
// Target Devices:  FPGA
// Tool Versions:   1v0
// Description:     Skeleton for doing echo test on device
// Dependencies:    None
//
// State: 	        Works! (System Test done: 16.01.2025)
// Improvements:    None
// Parameters:      BITWIDTH_IN --> Bitwidth of input data
//                  BITWIDTH_SYS --> Bitwidth of data bus on device
//                  BITWIDTH_HEAD --> Bitwidth of metadata (skeleton properties)
//////////////////////////////////////////////////////////////////////////////////


module SKELETON_ECHO_{§device_id}#(
	parameter BITWIDTH_IN = 5'd16,
    parameter BITWIDTH_SYS = 5'd16,
    parameter BITWIDTH_HEAD = 6'd32
)(
    input wire CLK_SYS,
    input wire nRST,
    input wire EN,
    input wire START_FLAG,
    input wire [BITWIDTH_SYS-'d1:0] DATA_IN,
    output wire [BITWIDTH_SYS-'d1:0] DATA_OUT,
    output wire [BITWIDTH_HEAD-'d7:0] DATA_HEAD,
    output wire DATA_VALID
);

	localparam BITWIDTH_OFFSET = BITWIDTH_SYS - BITWIDTH_IN;
    
    reg first_run_done;
    assign DATA_OUT = {DATA_IN[(BITWIDTH_SYS-'d1)-:BITWIDTH_IN}, {BITWIDTH_OFFSET{1'd0}}};
    assign DATA_HEAD = {4'd0, 6'd1, 6'd1, BITWIDTH_IN[4:0], BITWIDTH_IN[4:0]};
    assign DATA_VALID = first_run_done && !START_FLAG;
       
    // --- Control lines 
    always@(posedge CLK_SYS) begin
        if(~(nRST && EN)) begin
            first_run_done <= 1'd0;
        end else begin
            first_run_done <= (START_FLAG) ? 1'd1 : first_run_done;
        end
    end
endmodule
