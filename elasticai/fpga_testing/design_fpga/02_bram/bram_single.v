//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
//
// Create Date:     17.02.2023 23:08:27
// Copied on: 	    §{date_copy_created}
// Module Name:     Template for building a single-port BlockRAM on device
// Target Devices:  ASIC / FPGA
// Tool Versions:   1v0
// Processing:      Data applied on posedge CLK_RAM, handling to BRAM on posedge CLK_RAM
// Dependencies:    DATA_FILE is optional
//
// State: 	        Works!
// Improvements:    None
// Parameters:      BITWIDTH    --> Bitwidth of input data
//                  RAMWIDTH    --> Number of cells to store data
//                  DATA_FILE   --> String with path to file for initial writing (if "" zero)
// Information:     https://www.dsprelated.com/showarticle/1337.php
//////////////////////////////////////////////////////////////////////////////////

//`define BRAM_LOAD_EXTERNAL


// --- CODE FOR READING PREDEFINED DATA FROM EXTERNAL
// wire [RAMWIDTH* BITWIDTH-'d1:0] PREDEFINED;
// assign PREDEFINED = §{PREDEFINED};

module BRAM_SINGLE#(
    parameter BITWIDTH = 'd12,
    parameter RAMWIDTH = 'd32,
    parameter DATA_FILE = "C:/Git/denspp.translate/elasticai/creator_plugins/memory/verilog/bram_preload.mem"
)(
    input wire CLK_RAM,
    input wire EN,
    input wire WE,
    `ifdef BRAM_LOAD_EXTERNAL
        input wire [RAMWIDTH*BITWIDTH-'d1:'d0] PREDEFINED,
    `endif
    input wire [$clog2(RAMWIDTH)-'d1:'d0] ADR,
    input wire [BITWIDTH-'d1:'d0] DIN,
    output wire [BITWIDTH-'d1:'d0] DOUT   
);

    reg [BITWIDTH-'d1:'d0] bram_block [RAMWIDTH-'d1:'d0];    
    assign DOUT = (EN && !WE) ? bram_block[ADR] : 'd0;

    `ifndef BRAM_LOAD_EXTERNAL
        initial begin
            if(DATA_FILE != "") begin
                $readmemh(DATA_FILE, bram_block, 'd0, RAMWIDTH-'d1);
            end
        end
    `endif
           
    integer i0; 
    always @(posedge CLK_RAM) begin
        if(EN) begin
            if(WE) begin
                bram_block[ADR] <= DIN;
            end else begin
                bram_block[ADR] <= bram_block[ADR];
            end
        end else begin
            for(i0='d0; i0 < RAMWIDTH; i0 = i0 + 'd1) begin
                `ifdef BRAM_LOAD_EXTERNAL
                    bram_block[i0] <= PREDEFINED[i0*BITWIDTH+:BITWIDTH];
                `else
                    bram_block[i0] <= (DATA_FILE != "") ? bram_block[i0] : 'd0;
                `endif
            end
        end    
    end
endmodule
