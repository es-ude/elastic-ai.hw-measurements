//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 13.11.2020 14:08:53
// Design Name:     UDE-ES, AE
// Module Name:     FIR (OneMultiplier)
// Project Name: 
// Target Devices:  ASIC (Implementing and using the mutArrayS module)
//                  FPGA (Entfernen des mutArray und Einsetzen des DSP-Blocks)
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

module SKELETON_ECHO#(
    parameter BITWIDTH_DATA = 5'd16,
    parameter BITWIDTH_HEAD = 6'd32
)(
    input wire CLK_SYS,
    input wire nRST,
    input wire EN,
    input wire START_FLAG,
    input wire [BITWIDTH_DATA-'d1:0] DATA_IN,
    output wire [BITWIDTH_DATA-'d1:0] DATA_OUT,
    output wire [BITWIDTH_HEAD-'d7:0] DATA_HEAD,
    output wire DATA_VALID
);
    
    reg first_run_done;
    assign DATA_OUT = DATA_IN;
    assign DATA_HEAD = {4'd0, 6'd1, 6'd1, BITWIDTH_DATA[4:0], BITWIDTH_DATA[4:0]};
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
