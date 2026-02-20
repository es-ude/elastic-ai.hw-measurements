//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
//
// Create Date: 	21.10.2024 12:38:44
// Copied on: 	    11/12/2024, 09:41:16
// Module Name:     LUT Generator (full waveform)
// Target Devices:  ASIC, FPGA
// Tool Versions:   1v1
// Description:     Digital Direct Syntheziser with Analog Signal Waveforms (21 x 16 bit)
// Dependencies:    None
//
// State:		    Works! (System Test done: 07.11.2024 on Arty A7-35T with 22% usage)
// Improvements:    None
// Parameters:      BIT_WIDTH   --> Bitwidth of the output value
//                  LUT_WIDTH   --> Length of LUT for saving waveform
//                  WAIT_CYC    --> Number of clock cycles to wait before update output
//                  WAIT_WIDTH  --> Bitwidth for defining WAIT_CYC with external middleware (R/nW)
//////////////////////////////////////////////////////////////////////////////////
//`define LUT0_ACCESS_EXTERNAL
//`define LUT0_COUNT_EXTERNAL
`define LUT0_TRGG_EXTERNAL

// --- CODE FOR READING DATA FROM EXTERNAL
// wire  [21 * 16 - 'd1:0] LUT_ROM;
// assign LUT_ROM = {16'd32767, 16'd22642, 16'd13507, 16'd6258, 16'd1603, 16'd0, 16'd1603, 16'd6258, 16'd13507, 16'd22642, 16'd32768, 16'd42893, 16'd52028, 16'd59277, 16'd63932, 16'd65535, 16'd63932, 16'd59277, 16'd52028, 16'd42893, 16'd32768};

module LUT_WVF_GEN0#(
	parameter LUT_WIDTH = 10'd21,
	parameter BIT_WIDTH = 6'd16,
	`ifndef LUT0_COUNT_EXTERNAL
        parameter WAIT_CYC = 12'd477
    `else
        parameter WAIT_WIDTH = 10'd9
	`endif
)(
	input wire CLK_SYS,
	input wire nRST,
	input wire EN,
	`ifdef LUT0_TRGG_EXTERNAL
	    input wire TRGG_CNT_FLAG,
    `elsif LUT0_COUNT_EXTERNAL
        input wire [$clog2(LUT_WIDTH)-'d1:0] WAIT_CYC,
    `endif
    `ifdef LUT0_ACCESS_EXTERNAL
        input wire  [BIT_WIDTH* LUT_WIDTH - 'd1:0] LUT_ROM,
    `endif
	output wire  [BIT_WIDTH-'d1:0] LUT_VALUE,
	output wire LUT_END
);

    // --- Registers for counting and controlling
    wire increase_cnt_sine;
    reg [$clog2(LUT_WIDTH)-'d1:0] cnt_sine;
    `ifndef LUT0_TRGG_EXTERNAL
        `ifdef LUT0_COUNT_EXTERNAL
            reg [WAIT_WIDTH-'d1:0] cnt_wait;
        `else
            reg [$clog2(WAIT_CYC)-'d1:0] cnt_wait;
        `endif
        // --- Counter for Downsampling System Clock
        always@(posedge CLK_SYS) begin
            if(~(nRST && EN)) begin
                cnt_wait <= 'd0;
            end else begin
                if(cnt_wait == WAIT_CYC-'d1) begin
                    cnt_wait <= 'd0;
                end else begin
                    cnt_wait <= cnt_wait + 'd1;
                end
            end
        end
        assign increase_cnt_sine = (cnt_wait == WAIT_CYC-'d1);
    `else
        assign increase_cnt_sine = TRGG_CNT_FLAG;
    `endif

    // --- Processing LUT data
    assign LUT_END = (cnt_sine == (LUT_WIDTH-'d1));
    wire  [BIT_WIDTH-'d1:0] lut_ram [LUT_WIDTH-'d1:0];
    assign LUT_VALUE = lut_ram[cnt_sine];
    `ifdef LUT0_ACCESS_EXTERNAL
        genvar i0;
        for(i0 = 'd0; i0 < LUT_WIDTH; i0 = i0 + 'd1) begin
            assign lut_ram[i0] = LUT_ROM[i0*BIT_WIDTH+:BIT_WIDTH];
        end
    `else
        // --- Data save in BRAM
		assign lut_ram[0] = 16'd32768;
		assign lut_ram[1] = 16'd42893;
		assign lut_ram[2] = 16'd52028;
		assign lut_ram[3] = 16'd59277;
		assign lut_ram[4] = 16'd63932;
		assign lut_ram[5] = 16'd65535;
		assign lut_ram[6] = 16'd63932;
		assign lut_ram[7] = 16'd59277;
		assign lut_ram[8] = 16'd52028;
		assign lut_ram[9] = 16'd42893;
		assign lut_ram[10] = 16'd32768;
		assign lut_ram[11] = 16'd22642;
		assign lut_ram[12] = 16'd13507;
		assign lut_ram[13] = 16'd6258;
		assign lut_ram[14] = 16'd1603;
		assign lut_ram[15] = 16'd0;
		assign lut_ram[16] = 16'd1603;
		assign lut_ram[17] = 16'd6258;
		assign lut_ram[18] = 16'd13507;
		assign lut_ram[19] = 16'd22642;
		assign lut_ram[20] = 16'd32767;

    `endif

    // --- Counter for Getting LUT Value
    always@(posedge CLK_SYS) begin
        if(~(nRST && EN)) begin
            cnt_sine <= 'd0;
        end else begin
            if(increase_cnt_sine) begin
                cnt_sine <= (cnt_sine == LUT_WIDTH-'d1) ? 'd1 : cnt_sine + 'd1;
            end else begin
                cnt_sine <= cnt_sine;
            end
        end
    end

endmodule
