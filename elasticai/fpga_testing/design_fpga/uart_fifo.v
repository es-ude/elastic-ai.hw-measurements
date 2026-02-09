//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
//
// Create Date:     19.04.2023 18:25:50
// Copied on: 	    §{date_copy_created}
// Module Name:     UART FIFO Module for building complete communication procotocols
// Target Devices:  FPGA
// Tool Versions:   1v0
// Dependencies:    None
//
// State: 	        Tested!
// Improvements:    None
// Comments:        None
// Parameters:      DT_BITRATE  --> Clock cycles between sampling for extracting information
//////////////////////////////////////////////////////////////////////////////////

module UART_FIFO#(
    parameter FIFO_SIZE = 'd4
)(
    input wire CLK,
    input wire RSTN,
    input wire UART_RDY_FLAG,
    //Sliced data for UART module
    input wire [7:0] UART_DIN,
    output wire [7:0] UART_DOUT,
    //Transmitted data for FPGA
    input wire  ['d8*FIFO_SIZE-'d1:0] DATA_IN,
    output wire ['d8*FIFO_SIZE-'d1:0] DATA_OUT,
    //Control of FPGA modules
    output wire UART_START_FLAG,
    output wire FIFO_RDY
);

localparam STATE_IDLE = 2'd0, STATE_START = 2'd1, STATE_FIFO = 2'd2, STATE_STOP = 2'd3;

reg [1:0] state;
reg [3:0] cnt_uart;
reg [2:0] shift_uart;
reg [7:0] uart_fifo [FIFO_SIZE-'d1:0];
wire [7:0] data_fifo_in [FIFO_SIZE-'d1:0];

assign FIFO_RDY = !state;
assign UART_START_FLAG = (shift_uart[0] && !shift_uart[2]) && (cnt_uart != FIFO_SIZE);
assign UART_DOUT = uart_fifo[cnt_uart];

genvar i0;
for (i0 = 0; i0 < FIFO_SIZE; i0 = i0 + 1) begin
    assign DATA_OUT[(8*i0)+:8] = uart_fifo[i0];
    assign data_fifo_in[i0] = DATA_IN[(8*i0)+:8];
end

integer i1;
wire do_flag_pos, do_flag_neg;
assign do_flag_pos = (UART_RDY_FLAG && !shift_uart[0]);
assign do_flag_neg = (!shift_uart[0] && shift_uart[1]);

//############################### FIFO-Controller
always@(posedge CLK) begin
    if(~RSTN) begin
        shift_uart = 3'b111;
        state = STATE_IDLE;
        cnt_uart = 4'd0;
        for(i1 = 'd0; i1 < FIFO_SIZE; i1 = i1 + 'd1) begin
            uart_fifo[i1] <= 8'd0;
        end
    end else begin
        shift_uart <= {shift_uart[1:0], UART_RDY_FLAG};
        case(state) 
            STATE_IDLE: begin
                state <= (do_flag_neg) ? STATE_START : STATE_IDLE;
            end
            STATE_START: begin 
                state <= STATE_FIFO;
                for(i1 = 0; i1 < FIFO_SIZE; i1 = i1 + 'd1) begin
                    uart_fifo[i1] <= data_fifo_in[i1];
                end
            end
            STATE_FIFO: begin
                if(cnt_uart == FIFO_SIZE) begin
                    state <= STATE_STOP;
                    cnt_uart <= 4'd0;
                    for(i1 = 'd0; i1 < FIFO_SIZE; i1 = i1 + 'd1) begin
                        uart_fifo[i1] <= uart_fifo[i1];
                    end
                end else begin
                    state <= STATE_FIFO;
                    cnt_uart <= cnt_uart + ((do_flag_pos) ? 4'd1 : 4'd0);
                    uart_fifo[cnt_uart] <= (do_flag_pos) ? UART_DIN : uart_fifo[cnt_uart]; 
                end
            end
            STATE_STOP: begin
                state <= STATE_IDLE;
            end
        endcase           
    end    
end

endmodule
