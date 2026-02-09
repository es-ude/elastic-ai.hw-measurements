// UART_CNT_BAUDRATE = 216 --> UART_BAUD = 115.200
module TOP_MODULE#(
    parameter NUM_DUT = 3,
    parameter UART_CNT_BAUDRATE = 216,
    parameter UART_FIFO_BYTE_SIZE = 3,
    parameter TEST_ENV_ADR_WIDTH = 6,
    parameter TEST_ENV_DATA_BITWIDTH = 16
)(
    input wire          CLK_100MHz,
    input wire          RSTN,
    //General purpose I/O       
    output wire [3:0]   LED_TEST,
    output wire [7:0]   DEBUG,
    //Communications: UART
    output wire         UART_TX,
    input wire          UART_RX
);
    localparam TEST_HEAD_BITWIDTH = 6'd32;
    
    //Signals for UART module
    wire uart_mod_rdy, uart_data_rdy, uart_mod_start;
    wire [7:0] uart_data_in, uart_data_out;
    assign uart_mod_start = 1'd0;
    
    wire uart_fifo_rdy;
    wire ['d8* UART_FIFO_BYTE_SIZE -'d1:0] uart_fifo_din, uart_fifo_dout;
    
    wire dut_start_flag, dut_rdy, dut_rnw;  
    wire [$clog2(NUM_DUT)-'d1:0] dut_sel;
    wire [TEST_ENV_ADR_WIDTH-'d1:0] dut_adr;
    wire [TEST_ENV_DATA_BITWIDTH-'d1:0] dut_din, dut_dout;
    wire [TEST_HEAD_BITWIDTH-'d1:0] dut_header;
    
    //Interface for Debugging modules  
    assign LED_TEST[3:2] = {dut_rdy, uart_data_rdy};
    assign DEBUG = {dut_dout[TEST_ENV_DATA_BITWIDTH-'d1-:4], dut_start_flag, dut_rdy, uart_mod_rdy, uart_data_rdy};
    
    //##########################################################
    //UNTER-MODULE: DEVICE UNDER TEST    
    TEST_ENVIRONMENT#(
        .BITWIDTH_DATA(TEST_ENV_DATA_BITWIDTH), 
        .BITWIDTH_ADR(TEST_ENV_ADR_WIDTH), 
        .NUM_DUT(NUM_DUT), 
        .NUM_BITS_HEADER(TEST_HEAD_BITWIDTH), 
        .UINT_DATATYPE(1'd1)
    ) DUT(
        .CLK(CLK_100MHz),
        .RSTN(RSTN),
        .START_FLAG(dut_start_flag),
        .SEL(dut_sel),
        .ADR(dut_adr),
        .RnW(dut_rnw),
        .DATA_IN(dut_din),
        .DATA_OUT(dut_dout),
        .HEAD_INFO(dut_header),
        .RDY_FLAG(dut_rdy)    
    );
       
    //##########################################################    
    //UNTER-MODULE: Communication + DUT_Handler in DataHandler
    UART_COM#(UART_CNT_BAUDRATE) UART_MOD(
        .CLK(CLK_100MHz),
        .RSTN(RSTN),
        .start_flag(uart_mod_start),
        .DATA_TX(uart_data_out),
        .DATA_RX(uart_data_in),
        .RX(UART_RX),
        .TX(UART_TX),
        .DATA_RDY(uart_data_rdy),
        .MOD_RDY(uart_mod_rdy)        
    );
    UART_FIFO#(UART_FIFO_BYTE_SIZE) UART_FIFO(
        .CLK(CLK_100MHz),
        .RSTN(RSTN),
        .UART_RDY_FLAG(uart_data_rdy),
        .UART_DIN(uart_data_in),
        .UART_DOUT(uart_data_out),
        .DATA_IN(uart_fifo_din),
        .DATA_OUT(uart_fifo_dout),
        .UART_START_FLAG(),
        .FIFO_RDY(uart_fifo_rdy)  
    );
    UART_MIDDLEWARE#(
        .BYTE_SIZE(UART_FIFO_BYTE_SIZE), 
        .BITWIDTH_DATA(TEST_ENV_DATA_BITWIDTH),
        .BITWIDTH_ADR(TEST_ENV_ADR_WIDTH),
        .NUM_DUT(NUM_DUT),
        .BITWIDTH_HEAD(TEST_HEAD_BITWIDTH)
    ) MIDDLEWARE(
        .CLK(CLK_100MHz),
        .RSTN(RSTN),
        .DATA_RDY(uart_fifo_rdy),
        .DATA_IN(uart_fifo_dout),
        .DATA_OUT(uart_fifo_din),
        .LED_TEST(LED_TEST[1:0]),
        .DO_TEST(dut_start_flag),
        .DUT_SEL(dut_sel),
        .DUT_DIN(dut_din),
        .DUT_DOUT(dut_dout),
        .DUT_ADR(dut_adr),
        .DUT_RnW(dut_rnw),
        .DUT_RDY(dut_rdy),
        .DUT_HEADER(dut_header)
    );
    
endmodule
