//////////////////////////////////////////////////////////////////////////////////
// Company:         University of Duisburg-Essen, Intelligent Embedded Systems Lab
// Engineer:        AE
//
// Create Date:     09.09.2018 16:50:10
// Copied on: 	    §{date_copy_created}
// Module Name:     UART Physical Implementation 
// Target Devices:  FPGA
// Tool Versions:   1v0
// Processing:      Oversampling the RX/TX lines for protocol handling 
// Dependencies:    None
//
// State: 	        Tested!
// Improvements:    None
// Comments:        None
// Parameters:      DT_BITRATE  --> Clock cycles between sampling for extracting information
//////////////////////////////////////////////////////////////////////////////////
// Calculating the variable: DT_BITRATE = f_sys/(n* BAUDRATE) -1, mit f_sys = 100 MHz (=Sampling rate)
// Example #1: BAUDRATE = 115.200 (n = 4) --> 216
// Example #2: BAUDRATE = 115.200 (n = 4) --> 216
// Example #3: BAUDRATE = 921.600 (n = 4) --> 26


module UART_COM#(
	parameter DT_BITRATE = 'd26
)(
    input wire CLK,
    input wire RSTN,
    input wire start_flag,
    // --- Communication signals (from external device)
    input wire RX,
    output reg TX,
    // --- Controlling the Middleware / FIFO buffer (FPGA internal)
    input wire [7:0] DATA_TX,
    output wire [7:0] DATA_RX,
    output wire DATA_RDY,
    output wire MOD_RDY
);
    
    localparam UART_NSAMP = 3'd3;
    localparam STATE_IDLE = 2'd0, STATE_START = 2'd1, STATE_RW = 2'd2, STATE_STOP = 2'd3;
    
    reg [1:0] state;
    reg [7:0] bufferUART;
    reg [3:0] bit_transfer;
    
    reg [2:0] valRX;
    reg [$clog2(DT_BITRATE)-'d1:0] cnt_dt;
    reg [2:0] cnt_ovs;
    wire ovs_done_flag, cnt_done_flag, uart_done_flag;
    
    assign DATA_RX = (RSTN && DATA_RDY) ? bufferUART : 8'd0;

    assign MOD_RDY = (state == STATE_IDLE) && RSTN;
    assign DATA_RDY = (state == STATE_STOP || state == STATE_IDLE) && RSTN;
    
    assign cnt_done_flag = (cnt_dt == DT_BITRATE);
    assign ovs_done_flag = (cnt_ovs == UART_NSAMP);
    assign uart_done_flag = (bit_transfer == 4'd8);
    
    always@(posedge CLK) begin
        if(~RSTN) begin
            bufferUART <= 8'd0;
            state <= STATE_IDLE;
            cnt_dt <= 'd0;
            cnt_ovs <= 3'd0;
            bit_transfer <= 4'd0;
            TX <= 1'd1;
            valRX <= 3'd0;
        end else begin
            case(state)
                //Warten bis Nachricht oder 
                STATE_IDLE: begin
                    state <= (start_flag || !RX) ? STATE_START : STATE_IDLE;
                end
                //Senden des Start-Bits
                STATE_START: begin
                    TX <= 1'd0;
                    if(cnt_done_flag) begin
                        cnt_dt <= 'd0;
                        cnt_ovs <= (ovs_done_flag) ? 3'd0 : cnt_ovs + 3'd1;
                        state <= (ovs_done_flag) ? STATE_RW : STATE_START;
                        bit_transfer <= bit_transfer + ((ovs_done_flag) ? 4'd1 : 4'd0); 
                    end else begin
                        cnt_dt <= cnt_dt + 'd1;
                        cnt_ovs <= cnt_ovs;
                        state <= STATE_START;
                        bit_transfer <= bit_transfer;
                    end
                end
                //Datentransfer mit 4-facher Abtastung
                STATE_RW: begin
                    TX <= DATA_TX[bit_transfer-4'd1];
                    if(cnt_done_flag) begin
                        cnt_dt <= 'd0;
                        cnt_ovs <= (ovs_done_flag) ? 3'd0 : cnt_ovs + 3'd1;
                        state <= (uart_done_flag && ovs_done_flag) ? STATE_STOP : STATE_RW; 
                        bit_transfer <= bit_transfer + ((ovs_done_flag) ? 4'd1 : 4'd0);
                        valRX <= (ovs_done_flag) ? 3'd0 : valRX + RX;
                        bufferUART <= (ovs_done_flag) ? {valRX[1], bufferUART[7:1]} : bufferUART;
                    end else begin
                        cnt_dt <= cnt_dt + 'd1;
                        cnt_ovs <= cnt_ovs;
                        state <= state; 
                        bit_transfer <= bit_transfer;
                        valRX <= valRX;
                        bufferUART <= bufferUART;
                    end
                end
                //UART beenden mit dem Stop-Bit
                STATE_STOP: begin
                    TX <= 1'd1;
                    if(cnt_done_flag) begin
                        cnt_dt <= 'd0;
                        cnt_ovs <= (ovs_done_flag) ? 3'd0 : cnt_ovs + 3'd1;
                        state <= (ovs_done_flag) ? STATE_IDLE : STATE_STOP;  
                        bit_transfer <= 4'd0;
                    end else begin
                        cnt_dt <= cnt_dt + 'd1;
                        cnt_ovs <= cnt_ovs;
                        state <= STATE_STOP;
                        bit_transfer <= bit_transfer;
                    end
                end  
            endcase
        end
    end
endmodule
