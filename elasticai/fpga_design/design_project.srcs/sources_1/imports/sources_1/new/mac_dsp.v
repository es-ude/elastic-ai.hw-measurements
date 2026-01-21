//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
// 
// Create Date:     17.01.2025 08:11:51
// Copied on: 	    §{date_copy_created}
// Module Name:     DSP-based Multiply-Accumulate Operator
// Target Devices:  FPGA (using multiplier from DSP slice)
// Tool Versions:   1v0
// Description:     Performing a MAC Operation on Device (with Pipelined Multiplier and Parallisation)
// Processing:      Data applied on posedge clk
// Dependencies:    None
//
// State: 	        Works! (System Test done: 22.01.2025 on Arty A7-35T with 20% usage)
// Improvements:    - Actual version supports parallel multiplication up to 8, automatic approach is missing
//                  - Implement N-bit Carry Save Adder before FF-Sampling (less resources and better timing?)
// Parameters:      INPUT_BITWIDTH --> Bitwidth of input data
//                  INPUT_NUM_DATA --> Length of used data
//                  NUM_MULT_PARALLEL --> Number of used multiplier in parallel
//////////////////////////////////////////////////////////////////////////////////

module MAC_DSP#(
    parameter INPUT_BITWIDTH = 6'd8,
    parameter INPUT_NUM_DATA = 12'd2,
    parameter NUM_MULT_PARALLEL = 4'd2
)(
    input wire CLK_SYS,
    input wire RSTN,
    input wire EN,
    input wire START_CALC_FLAG,
    input wire signed [INPUT_BITWIDTH -'d1:0] IN_BIAS,
    input wire signed [INPUT_NUM_DATA* INPUT_BITWIDTH -'d1:0] IN_WEIGHTS,
    input wire signed [INPUT_NUM_DATA* INPUT_BITWIDTH -'d1:0] IN_DATA,
    output wire signed [2* INPUT_BITWIDTH -'d1:0] OUT_DATA,
    output wire DATA_VALID,
    output reg DATA_RDY
);

    // --- Local parameter for configuring the pipeline and parallisation of MAC
    localparam NUM_K_PIPELINE_STAGE = 4'd2;
    localparam NUM_CYC_COMPLETE_WOPAD = INPUT_NUM_DATA / NUM_MULT_PARALLEL;
    localparam NUM_ZERO_PADDING = INPUT_NUM_DATA - NUM_CYC_COMPLETE_WOPAD * NUM_MULT_PARALLEL;
    localparam NUM_CYC_COMPLETE = (INPUT_NUM_DATA + NUM_ZERO_PADDING) / NUM_MULT_PARALLEL;
    localparam NUM_CYC_CNTSTOP = NUM_CYC_COMPLETE + NUM_K_PIPELINE_STAGE - 'd1;
    localparam NUM_BITWIDTH_MAC = 2* INPUT_BITWIDTH + NUM_MULT_PARALLEL;

    // --- Definition of Padded Input
    wire [(INPUT_NUM_DATA + NUM_ZERO_PADDING)* INPUT_BITWIDTH -'d1:0] padded_input_data;
    wire [(INPUT_NUM_DATA + NUM_ZERO_PADDING)* INPUT_BITWIDTH -'d1:0] padded_input_wght;
    assign padded_input_data = {{NUM_ZERO_PADDING* INPUT_BITWIDTH{1'd0}}, IN_DATA};
    assign padded_input_wght = {{NUM_ZERO_PADDING* INPUT_BITWIDTH{1'd0}}, IN_WEIGHTS};

    // --- Definition of internal signals and register
    reg [$clog2(NUM_CYC_CNTSTOP):0] cnt_cyc_calc;
    reg signed [INPUT_BITWIDTH-'d1:0] pipeline_input_a [NUM_MULT_PARALLEL-'d1:0];
    reg signed [INPUT_BITWIDTH-'d1:0] pipeline_input_b [NUM_MULT_PARALLEL-'d1:0];
    reg signed [2* INPUT_BITWIDTH-'d1:0] pipeline_output [NUM_MULT_PARALLEL-'d1:0];
    reg signed [NUM_BITWIDTH_MAC-'d1:0] mac_out;


    wire do_shift_data;
    assign do_shift_data = ~((cnt_cyc_calc == NUM_CYC_CNTSTOP - 'd1) || (cnt_cyc_calc == NUM_CYC_CNTSTOP));
    assign OUT_DATA = mac_out[2*INPUT_BITWIDTH-'d1:0];

    // --- Range Violation Checker
    ADDER_RANGE_DTCT#(2*INPUT_BITWIDTH-'d1, NUM_MULT_PARALLEL-'d1, 1'd1) CHCK(
        .A(mac_out),
        .UPPER_LIMIT(),
        .DOWNER_LIMIT(),
        .DATA_VALID(DATA_VALID)
    );

    // --- Control device for pipeline multiplication
    integer i0, k1;
    always@(posedge CLK_SYS or negedge RSTN) begin
        if(~RSTN) begin
            DATA_RDY <= 1'd0;
            cnt_cyc_calc <= 'd0;
            for(i0 = 'd0; i0 < NUM_MULT_PARALLEL; i0 = i0 + 'd1) begin
                pipeline_input_a[i0] <= 'd0;
                pipeline_input_b[i0] <= 'd0;
                pipeline_output[i0] <= 'd0;
            end
            mac_out <= 'd0;
        end else begin
            DATA_RDY <= (START_CALC_FLAG && EN) ? 1'd0 : ((cnt_cyc_calc == NUM_CYC_CNTSTOP) ? 'd1 : DATA_RDY);
            if(EN) begin
                if(DATA_RDY) begin
                    // --- State #0: Hold data
                    cnt_cyc_calc <= 'd0;
                    for(i0 = 'd0; i0 < NUM_MULT_PARALLEL; i0 = i0 + 'd1) begin
                        pipeline_input_a[i0] <= pipeline_input_a[i0];
                        pipeline_input_b[i0] <= pipeline_input_b[i0];
                        pipeline_output[i0] <= pipeline_output[i0];
                    end
                    mac_out <= mac_out;
                 end else begin
                    // --- State #1: Do Calculation
                    cnt_cyc_calc <= (cnt_cyc_calc == NUM_CYC_CNTSTOP) ? 'd0 : cnt_cyc_calc + 'd1;
                    for(i0 = 'd0; i0 < NUM_MULT_PARALLEL; i0 = i0 + 'd1) begin
                        pipeline_input_a[i0] <= (do_shift_data) ? padded_input_data[(cnt_cyc_calc + i0 * NUM_CYC_COMPLETE)* INPUT_BITWIDTH+: INPUT_BITWIDTH] : 'd0;
                        pipeline_input_b[i0] <= (do_shift_data) ? padded_input_wght[(cnt_cyc_calc + i0 * NUM_CYC_COMPLETE)* INPUT_BITWIDTH+: INPUT_BITWIDTH] : 'd0;
                        pipeline_output[i0] <= pipeline_input_a[i0] * pipeline_input_b[i0];
                    end
                    case(NUM_MULT_PARALLEL)
                        4'd2:
                            mac_out <= (cnt_cyc_calc == 'd0 && ~DATA_RDY) ? {{(INPUT_BITWIDTH){IN_BIAS[INPUT_BITWIDTH-'d1]}}, IN_BIAS} : mac_out + pipeline_output[0] + pipeline_output[1];
                        4'd3:
                            mac_out <= (cnt_cyc_calc == 'd0 && ~DATA_RDY) ? {{(INPUT_BITWIDTH){IN_BIAS[INPUT_BITWIDTH-'d1]}}, IN_BIAS} : mac_out + pipeline_output[0] + pipeline_output[1] + pipeline_output[2];
                        4'd4:
                            mac_out <= (cnt_cyc_calc == 'd0 && ~DATA_RDY) ? {{(INPUT_BITWIDTH){IN_BIAS[INPUT_BITWIDTH-'d1]}}, IN_BIAS} : mac_out + pipeline_output[0] + pipeline_output[1] + pipeline_output[2] + pipeline_output[3];
                        4'd5:
                            mac_out <= (cnt_cyc_calc == 'd0 && ~DATA_RDY) ? {{(INPUT_BITWIDTH){IN_BIAS[INPUT_BITWIDTH-'d1]}}, IN_BIAS} : mac_out + pipeline_output[0] + pipeline_output[1] + pipeline_output[2] + pipeline_output[3] + pipeline_output[4];
                        4'd6:
                            mac_out <= (cnt_cyc_calc == 'd0 && ~DATA_RDY) ? {{(INPUT_BITWIDTH){IN_BIAS[INPUT_BITWIDTH-'d1]}}, IN_BIAS} : mac_out + pipeline_output[0] + pipeline_output[1] + pipeline_output[2] + pipeline_output[3] + pipeline_output[4] + pipeline_output[5];
                        4'd7:
                            mac_out <= (cnt_cyc_calc == 'd0 && ~DATA_RDY) ? {{(INPUT_BITWIDTH){IN_BIAS[INPUT_BITWIDTH-'d1]}}, IN_BIAS} : mac_out + pipeline_output[0] + pipeline_output[1] + pipeline_output[2] + pipeline_output[3] + pipeline_output[4] + pipeline_output[5] + pipeline_output[6];
                        4'd8:
                            mac_out <= (cnt_cyc_calc == 'd0 && ~DATA_RDY) ? {{(INPUT_BITWIDTH){IN_BIAS[INPUT_BITWIDTH-'d1]}}, IN_BIAS} : mac_out + pipeline_output[0] + pipeline_output[1] + pipeline_output[2] + pipeline_output[3] + pipeline_output[4] + pipeline_output[5] + pipeline_output[6] + pipeline_output[7];
                        default:
                            mac_out <= (cnt_cyc_calc == 'd0 && ~DATA_RDY) ? {{(INPUT_BITWIDTH){IN_BIAS[INPUT_BITWIDTH-'d1]}}, IN_BIAS} : mac_out + pipeline_output[0];
                    endcase
                end
            end else begin
                // --- State #2: Disable
                DATA_RDY <= 1'd0;
                cnt_cyc_calc <= 'd0;
                for(i0 = 'd0; i0 < NUM_MULT_PARALLEL; i0 = i0 + 'd1) begin
                    pipeline_input_a[i0] <= 'd0;
                    pipeline_input_b[i0] <= 'd0;
                    pipeline_output[i0] <= 'd0;
                end
                mac_out <= 'd0;
            end
        end
    end
endmodule
