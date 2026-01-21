module DUT#(
    parameter BITWIDTH_DATA = 5'd16, 
    parameter BITWIDTH_ADR = 5'd6,
    parameter NUM_DUT = 6'd3,
    parameter NUM_BITS_HEADER = 6'd32,
    parameter UINT_DATATYPE = 1'd1
)(
    input wire CLK,
    input wire nRST,
    input wire START_FLAG,
    input wire [$clog2(NUM_DUT)-'d1:0] SEL,
    input wire [BITWIDTH_ADR-'d1:0] ADR,
    input wire RnW,
    input wire [BITWIDTH_DATA-'d1:0] DATA_IN,
    output wire [BITWIDTH_DATA-'d1:0] DATA_OUT,
    output wire [NUM_BITS_HEADER-'d1:0] HEAD_INFO, 
    output wire RDY_FLAG
);
    //################## CONTROL LINES ################## 
    wire [BITWIDTH_DATA-'d1:0] dout [NUM_DUT-'d1:0];
    assign DATA_OUT = dout[SEL]; 

    wire [NUM_DUT-'d1:0] rdy_filt;
    assign RDY_FLAG = rdy_filt[SEL];
    
    //* This variable contains information about the module for read-in in Python 
    //  - NUM_DUTS (6-bits):        Total number of DUTs available in this function (automated added here)
    //  - DUT_TPYE (4-bits):        0 = Echo, 1 = Multiplier, 2 = Division, 3 = ROM, 4 = RAM, 5 = Filter, 6 = Processor, 7 = Skeleton (elasticAI.creator)
    //  - NUM_INPUTS (6-bits):      Number of used inputs
    //  - NUM_OUTPUTS (6-bits):     Number of used outputs
    //  - BITWIDTH_IN (5-bits):     Bitwidth of input data
    //  - BITWIDTH_OUT (5-bits):    Bitwidth of output data
    wire [NUM_BITS_HEADER-'d7:0] head_array [NUM_DUT-'d1:0];
    assign HEAD_INFO = {NUM_DUT, head_array[SEL]};
   
    //################## List with DUT ################## 
    SKELETON_ECHO#(BITWIDTH_DATA, NUM_BITS_HEADER) DUT0(
        .CLK_SYS(CLK),
        .nRST(nRST),
        .EN(SEL == 'd0),
        .START_FLAG(START_FLAG),
        .DATA_IN(DATA_IN),
        .DATA_OUT(dout[0]),
        .DATA_HEAD(head_array[0]),
        .DATA_VALID(rdy_filt[0])
    );    
        
    SKELETON_ROM#('d16, BITWIDTH_DATA, NUM_BITS_HEADER) DUT1(
        .CLK_SYS(CLK),
        .nRST(nRST),
		.EN(SEL == 'd1),
		.TRGG_START_CALC(START_FLAG),
		.DATA_IN(DATA_IN),
		.DATA_OUT(dout[1]),
		.DATA_HEAD(head_array[1]),
		.RDY(rdy_filt[1])
    );    
    	
    SKELETON_FILT#('d16, BITWIDTH_DATA, NUM_BITS_HEADER) DUT2(
        .CLK_SYS(CLK),
        .nRST(nRST),
		.EN(SEL == 'd2),
		.TRGG_START_CALC(START_FLAG),
		.DATA_IN(DATA_IN),
		.DATA_OUT(dout[2]),
		.DATA_HEAD(head_array[2]),
		.RDY(rdy_filt[2])
    );
        
endmodule
