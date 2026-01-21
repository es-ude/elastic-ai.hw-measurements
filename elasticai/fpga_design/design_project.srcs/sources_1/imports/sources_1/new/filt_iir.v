//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
// 
// Create Date:     15.10.2024 13:26:51
// Copied on: 	    10/29/2024, 23:09:08
// Module Name:     IIR Filter (1st and 2nd Order / SOS-Filter, (five clock with one multiplier))
// Target Devices:  ASIC (Implementing and using the mutArrayS module)
//                  FPGA (Using DSP block for multiplication)
// Tool Versions:   1v2
// Description:     Structure: Direct Form 2, signed integer operation
// Processing:      Data applied on posedge clk
// Dependencies:    mutArrayS with custom-made multiplier (for ASIC)
// 
// State: 	        Works! (System Test done: 29.10.2024 on Arty A7-35T with 20% usage)
// Improvements:    Implement the IIR filter in Direct Form 2 (less memory usage)
// Parameters:      BITWIDTH_DATA --> Bitwidth of input data
//////////////////////////////////////////////////////////////////////////////////
`define IIR_1_USE_INT_WEIGHTS
//`define IIR_1_USE_EXT_MAC


// Input values are integer or unsigned with size of BITWIDTH_DATA (no fixed point)
// Internal operation with signed values and all weights have fraction width of BITWIDTH_DATA-'d2;
module Filter_IIR_1#(
    parameter BITWIDTH_DATA = 6'd16
)(
    // Global control signals
    input wire CLK,
    input wire nRST,
    input wire EN,
    input wire START_FLAG,
    // Filter coefficients input (b0, b1, b2, -a1, -a2)
	`ifndef IIR_1_USE_INT_WEIGHTS
		input wire signed ['d5* BITWIDTH_DATA-'d1:0] FILT_WEIGHTS,
	`endif
	`ifdef IIR_1_USE_EXT_MAC
	    output wire signed ['d5* BITWIDTH_DATA-'d1:0] MAC_INPUT_A,   
	    output wire signed ['d5* BITWIDTH_DATA-'d1:0] MAC_INPUT_B,
	    output wire MAC_START_FLAG,
	    input wire signed ['d2* BITWIDTH_DATA-'d1:0] MAC_OUTPUT,   
	    input wire MAC_DRDY,
	    input wire MAC_DVALID,
	`endif
    // Data I/O
    input wire signed [BITWIDTH_DATA-'d1:0] DATA_IN,
    output wire signed [BITWIDTH_DATA-'d1:0] DATA_OUT,
    output wire DATA_RDY,
    output wire DATA_VALID
);

    //################## Internal signals
    localparam UPPER_MASK = 2*BITWIDTH_DATA - 'd3;
    localparam STATE_IDLE = 2'd0, STATE_MAC = 2'd1, STATE_CALC = 2'd2, STATE_TAPS = 2'd3;

    reg [1:0] state;
    reg signed [BITWIDTH_DATA-'d1:0] tap_input [1:0], tap_output [1:0];

    wire mac_drdy_int, mac_dvalid_int;
    wire signed [BITWIDTH_DATA-'d1:0] coeff [4:0];
    wire ['d5* BITWIDTH_DATA-'d1:0] filt_data, filt_coeff;
    wire signed [2* BITWIDTH_DATA-'d1:0] mac_out;
    
    assign DATA_OUT = tap_output[0];
    assign DATA_RDY = (state == STATE_IDLE) && mac_rdy_int;
    assign DATA_VALID = (state == STATE_IDLE) && mac_dvalid_int;
   
    //################## Choicing the multiplier module ##################
    // --- Control signals and data flow to Multiplier
    assign filt_data = {tap_output[1], tap_output[0], tap_input[1], tap_input[0], DATA_IN[BITWIDTH_DATA-'d1:0]};
    assign filt_coeff = {coeff[4], coeff[3], coeff[2], coeff[1], coeff[0]};
    
    //Choicing the multiplier module
    // Using DSP-based MAC Operator (incl. Pipelining and Parallelisation)
    `ifndef IIR_1_USE_EXT_MAC
        MAC_DSP#(BITWIDTH_DATA, 'd5, 'd1) MAC(
            .CLK_SYS(CLK),
            .RSTN(nRST),
            .EN(EN),
            .START_CALC_FLAG(state == STATE_MAC),
            .IN_BIAS('d0),
            .IN_WEIGHTS(filt_coeff),
            .IN_DATA(filt_data),
            .OUT_DATA(mac_out),
            .DATA_RDY(mac_rdy_int),
            .DATA_VALID(mac_dvalid_int)    
        );
     `else
        assign MAC_INPUT_A = filt_coeff;
        assign MAC_INPUT_B = filt_data;
        assign MAC_START_FLAG = (state == STATE_MAC);
        assign mac_out = MAC_OUTPUT;
        assign mac_drdy_int = MAC_DRDY;
        assign mac_dvalid_int = MAC_DVALID;
     
     `endif

    //################## Structure of Direct Form 1 Filter ##################
    integer i0;
    //Control-Structure
    always@(posedge CLK) begin
        if(~(nRST && EN)) begin
            state <= STATE_IDLE;
            for(i0 = 'd0; i0 < 'd2; i0 = i0 + 'd1) begin
                tap_input[i0] <= 'd0;
                tap_output[i0] <= 'd0;
            end
        end else begin
            case(state)
                STATE_IDLE: begin
                    state = (START_FLAG) ? STATE_MAC : STATE_IDLE;
                end
                STATE_MAC: begin
                    state <= STATE_CALC;
                end
                STATE_CALC: begin
                    state <= (mac_rdy_int && mac_dvalid_int) ? STATE_TAPS : STATE_CALC;
                end
                STATE_TAPS: begin
                    tap_input[0] <= DATA_IN[BITWIDTH_DATA-'d1:0];
                    tap_input[1] <= tap_input[0];
                    tap_output[0] <= mac_out[UPPER_MASK-:BITWIDTH_DATA];
                    tap_output[1] <= tap_output[0];
                    state <= STATE_IDLE;
                end
            endcase
        end
    end

    //################## Definition of the weights ##################
    // Filter coefficients input (b0, b1, b2, -a1, -a2), a0 is ignored due to 1
    `ifndef IIR_1_USE_INT_WEIGHTS
	   genvar i0;
		for(i0 = 0; i0 < 5; i0 = i0 +1) begin
			assign coeff[i0] = FILT_WEIGHTS[i0 * BITWIDTH_DATA+:BITWIDTH_DATA];
		end
    `else
        //--- Used filter coefficients (low, butter) with 100 Hz @ 1000.0 Hz
		assign coeff[0] = 16'h0451;	//coeff_b[0] = 0.06744384765625
		assign coeff[1] = 16'h08A2;	//coeff_b[1] = 0.1348876953125
		assign coeff[2] = 16'h0451;	//coeff_b[2] = 0.06744384765625
		assign coeff[3] = 16'h4926;	//coeff_a[1] = 1.1429443359375
		assign coeff[4] = 16'hE595;	//coeff_a[2] = -0.41278076171875

	`endif
endmodule
