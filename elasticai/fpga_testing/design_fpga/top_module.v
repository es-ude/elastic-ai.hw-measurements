// UART_CNT_BAUDRATE = 216 --> UART_BAUD = 115.200
module TOP_MODULE#(
    parameter NUM_DUT = 3,
    parameter UART_CNT_BAUDRATE = 216,
    parameter UART_FIFO_BYTE_SIZE = 3,
    parameter TEST_ENV_CMDS_BITWIDTH = 2,
    parameter TEST_ENV_ADR_WIDTH = 6,
    parameter TEST_ENV_DATA_BITWIDTH = 16
)(
    // --- Global signals
    input wire          CLK_100MHz,
    input wire          RSTN,
    // --- General purpose I/O
    output wire [3:0]   LED_TEST,
    output wire [7:0]   DEBUG,
    // --- UART Communication
    output wire         UART_TX,
    input wire          UART_RX
);
    localparam TEST_HEAD_BITWIDTH = 6'd32;
    localparam UART_BITWIDTH = 8;
    
    //Signals for UART module
    wire uart_mod_rdy, uart_mod_start;
    wire [UART_BITWIDTH-'d1:0] data_uart_to_fifo, data_fifo_to_uart;
    
    wire uart_fifo_rdy;
    wire [UART_BITWIDTH*UART_FIFO_BYTE_SIZE -'d1:0] data_fifo_to_mid, data_mid_to_fifo;
    
    wire dut_start_flag, dut_rdy, dut_rnw;  
    wire [$clog2(NUM_DUT):0] dut_sel;
    wire [TEST_ENV_ADR_WIDTH-'d1:0] dut_adr;
    wire [TEST_ENV_DATA_BITWIDTH-'d1:0] dut_din, dut_dout;
    wire [TEST_HEAD_BITWIDTH-'d1:0] dut_header;
    
    //Interface for Debugging modules  
    assign LED_TEST[3:1] = {dut_rdy, dut_sel[0], dut_start_flag};
    assign DEBUG = {dut_dout[TEST_ENV_DATA_BITWIDTH-'d1-:5], dut_start_flag, dut_rdy, uart_mod_rdy};
    
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
    UART_COM#(
        .BITRATE(UART_CNT_BAUDRATE),
        .BITWIDTH(UART_BITWIDTH),
        .NSAMP(4)
    ) UART_MOD (
        .CLK_SYS(CLK_100MHz),
        .RSTN(RSTN),
        .RX(UART_RX),
        .TX(UART_TX),
        .UART_START_FLAG(uart_mod_start),
        .UART_DIN(data_fifo_to_uart),
        .UART_DOUT(data_uart_to_fifo),
        .UART_RDY(uart_mod_rdy)
    );
    UART_FIFO#(
        .FIFO_SIZE(UART_FIFO_BYTE_SIZE),
        .BITWIDTH(UART_BITWIDTH)
    ) UART_FIFO(
        .CLK_SYS(CLK_100MHz),
        .RSTN(RSTN),
        .START_FLAG(1'd0),
        .UART_START_FLAG(uart_mod_start),
        .UART_RDY_FLAG(uart_mod_rdy),
        .UART_DIN(data_uart_to_fifo),
        .UART_DOUT(data_fifo_to_uart),
        .FIFO_IN(data_mid_to_fifo),
        .FIFO_OUT(data_fifo_to_mid),
        .FIFO_RDY(uart_fifo_rdy)  
    );
    UART_MIDDLEWARE#(
        .FIFO_SIZE(UART_FIFO_BYTE_SIZE),
        .BITWIDTH(UART_BITWIDTH),
        .BITWIDTH_CMDS(TEST_ENV_CMDS_BITWIDTH),
        .BITWIDTH_DATA(TEST_ENV_DATA_BITWIDTH),
        .BITWIDTH_ADR(TEST_ENV_ADR_WIDTH),
        .BITWIDTH_HEAD(TEST_HEAD_BITWIDTH),
        .NUM_DUT(NUM_DUT)
    ) MIDDLEWARE(
        .CLK_SYS(CLK_100MHz),
        .RSTN(RSTN),
        .FIFO_RDY(uart_fifo_rdy),
        .FIFO_DIN(data_fifo_to_mid),
        .FIFO_DOUT(data_mid_to_fifo),
        .LED_CONTROL(LED_TEST[0]),
        .DUT_DO_TEST(dut_start_flag),
        .DUT_SEL(dut_sel),
        .DUT_DIN(dut_din),
        .DUT_DOUT(dut_dout),
        .DUT_ADR(dut_adr),
        .DUT_RnW(dut_rnw),
        .DUT_HEADER(dut_header)
    );
endmodule
