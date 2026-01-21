//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10.05.2020 13:41:09
// Design Name: 
// Module Name: USART_DataHandler
// Project Name: 
// Target Devices: 
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

// ------------------------------- DATA FRAME ---------------------------------------------------------------
// # ---- CMD (2 bits)----  # ---- ADR (BITWIDTH_ADR) ----          # ---- DATA (BITWIDTH_DATA) ----        #
// # 0: REG_DUT_CNTL        # X | LED_TEST | DO_DUT_SEL | DO_TEST   # NUM_DUT (DO_DUT_SEL) | DATA (DO_TEST) #
// # 1: REG_DUT_WR          # ---- ADR ----                         # ---- DATA ----                        #
// # 2: REG_DUT_RD          # ---- ADR ----                         # ---- DATA ----                        #
// # 3: REG_HEAD_RD         # ---- ADR ----                         # xxxxxx                                #
// ------------------------------- DATA FRAME ---------------------------------------------------------------

module COM_DataHandler#(
    parameter BITWIDTH_DATA = 5'd16, 
    parameter BITWIDTH_ADR = 5'd6, 
    parameter BYTE_SIZE = 5'd3, 
    parameter NUM_DUT = 6'd5,
    parameter BITWIDTH_HEADER = 6'd32
)(
    //Control signals
    input wire                              CLK,
    input wire                              nRST,
    input wire                              DATA_RDY,
    input wire ['d8* BYTE_SIZE-'d1:0]       DATA_IN,
    output wire ['d8* BYTE_SIZE-'d1:0]      DATA_OUT,
    //Output signals
    output wire [1:0]                       LED_TEST,
    output wire                             DO_TEST,
    output reg [$clog2(NUM_DUT)-'d1:0]      DUT_SEL,
    output reg [BITWIDTH_DATA-'d1:0]        DUT_DIN,
    input wire [BITWIDTH_DATA-'d1:0]        DUT_DOUT,
    output wire [BITWIDTH_ADR-'d1:0]        DUT_ADR,
    output wire                             DUT_RnW,
    input wire                              DUT_RDY,
    input wire [BITWIDTH_HEADER-'d1:0]      DUT_HEADER
);

localparam REG_DUT_CNTL = 2'd0, REG_DUT_WR = 2'd1, REG_DUT_RD = 2'd2, REG_HEADER = 2'd3;
localparam BITWIDTH_CMDS = 2'd2;

// --- Definitions of control lines
reg [1:0] shift_drdy;
reg shift_test, led_active, trigger_flag;
wire drdy_posflag0, drdy_posflag1;

assign DO_TEST = trigger_flag ^ shift_test;
assign LED_TEST = {DUT_RDY, led_active};
assign drdy_posflag0 = DATA_RDY && !shift_drdy[0];
assign drdy_posflag1 = DATA_RDY && !shift_drdy[1];

// --- Slicing header information
localparam NUM_HEAD_TRANSMISSION = $clog2(BITWIDTH_HEADER) - $clog2(BITWIDTH_DATA);
wire [BITWIDTH_DATA-'d1:0] data_head_send [NUM_HEAD_TRANSMISSION:0];
genvar i1;
for(i1 = 'd0; i1 <= NUM_HEAD_TRANSMISSION; i1 = i1 + 'd1) begin
    assign data_head_send[i1] = DUT_HEADER[i1* BITWIDTH_DATA+:BITWIDTH_DATA];
end

// --- Data processing from/to UART FIFO buffer
wire ['d8* BYTE_SIZE -'d1:0] data_from_uart_fifo;
reg ['d8* BYTE_SIZE -'d1:0] data_to_uart_fifo;
wire [BITWIDTH_CMDS-'d1:0] sel_cmds;
wire [BITWIDTH_DATA-'d1:0] sel_data;

genvar i0;
for(i0 = 'd0; i0 < BYTE_SIZE; i0 = i0 + 'd1) begin
    assign data_from_uart_fifo[i0*'d8+:'d8] = (DATA_RDY) ? DATA_IN[(BYTE_SIZE-'d1-i0)* 'd8+:'d8] : 8'd0;
    assign DATA_OUT[i0*'d8+:'d8] = data_to_uart_fifo[(BYTE_SIZE-'d1-i0)* 'd8+:'d8];
end

// --- Data handler for Test module
assign sel_cmds = data_from_uart_fifo[(BITWIDTH_DATA+BITWIDTH_ADR)+:BITWIDTH_CMDS];
assign DUT_ADR = data_from_uart_fifo[BITWIDTH_DATA+:BITWIDTH_ADR];
assign sel_data =  data_from_uart_fifo[0+:BITWIDTH_DATA];
assign DUT_RnW = ~(sel_cmds == REG_DUT_WR);

always@(posedge CLK) begin
    if(!nRST) begin
        data_to_uart_fifo <= 'd0;
        shift_drdy <= 2'b11;
        shift_test <= 1'd0;
        trigger_flag <= 1'd0;
        DUT_DIN <= 'd0;
        DUT_SEL <= 'd0;
        led_active <= 1'd0;
    end else begin
        data_to_uart_fifo <= (drdy_posflag1) ? {sel_cmds, DUT_ADR, ((sel_cmds == REG_HEADER) ? data_head_send[DUT_ADR] : DUT_DOUT)} : data_to_uart_fifo;
        shift_drdy <= {shift_drdy[0], DATA_RDY};
        shift_test <= trigger_flag;
        
        //Implementiertes Datenprotokoll
        led_active      <= (drdy_posflag0 && sel_cmds == REG_DUT_CNTL && DUT_ADR[2])                                 ? ~led_active                      : led_active;
        trigger_flag    <= (drdy_posflag0 && sel_cmds == REG_DUT_CNTL && DUT_ADR[0])                                 ? ~trigger_flag                     : trigger_flag;
        DUT_SEL         <= (drdy_posflag0 && sel_cmds == REG_DUT_CNTL && DUT_ADR[1])                                 ? sel_data[$clog2(NUM_DUT)-'d1:0]   : DUT_SEL;
        DUT_DIN         <= (drdy_posflag0 && ((sel_cmds == REG_DUT_CNTL && DUT_ADR[0]) || sel_cmds == REG_DUT_WR))   ? sel_data                          : DUT_DIN;
    end 
end

endmodule