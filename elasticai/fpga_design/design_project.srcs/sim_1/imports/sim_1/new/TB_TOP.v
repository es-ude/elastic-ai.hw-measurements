`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 12.11.2020 15:30:17
// Design Name: 
// Module Name: TB_TOP
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


module TB_TOP();
    localparam FIFO_BYTE_SIZE = 'd3, BIT_WIDTH = 'd16, WAIT_CYC_UART = 'd100_000;
    localparam WAIT_CLK_CYC = 'd5, N_LUT_SIZE = 8'd21;

    reg CLK_100MHz, nRST, UART_START;
    wire UART_RX, UART_TX, UART_MOD_RDY;
    reg [1:0] UART_CNT;
    reg ['d8* (FIFO_BYTE_SIZE)-'d1:0] UART_DATA_TO, UART_DATA_FROM;
    reg ['d8* (FIFO_BYTE_SIZE)-'d1:0] UART_BACK_REAL;
    wire [15:0] UART_BACK_DATA;
    reg [7:0] UART_DIN;
    wire [7:0] UART_RETURN;
    wire [3:0] LED_TEST;
    wire [7:0] DEBUG;
    
    // --- Control scheme for clk and rst
	always begin
		#(WAIT_CLK_CYC) CLK_100MHz = ~CLK_100MHz;
	end
	
	always@(posedge UART_MOD_RDY or negedge nRST) begin
	   if(~nRST) begin
	       UART_DATA_FROM = 'd0;
	       UART_CNT = 'd0;
	   end else begin
	       UART_DATA_FROM[('d3-UART_CNT)*8+:8] = UART_RETURN;
	       UART_CNT = (UART_CNT == 'd3) ? 'd1 : UART_CNT + 'd1;
	   end
	end
	always@(posedge (UART_CNT == 'd1) or negedge nRST) begin
	   UART_BACK_REAL = (~nRST) ? 'd0 : UART_DATA_FROM;
	end 
	assign UART_BACK_DATA = UART_BACK_REAL[15:0];
	
    // --- Modul instanziation
    USART#('d216) UART_EXT(
        .CLK(CLK_100MHz),
        .nRST(nRST),
        .start_flag(UART_START),
        .DATA_TX(UART_DIN),
        .DATA_RX(UART_RETURN),
        .RX(UART_RX),
        .TX(UART_TX),
        .DATA_RDY(),
        .MOD_RDY(UART_MOD_RDY)    
    );
    
    TOP_MODUL DUT(
        .CLK_100MHz(CLK_100MHz),
        .nRST(nRST),
        .LED_TEST(LED_TEST),
        .DEBUG(DEBUG),
        .UART_RX(UART_TX),
        .UART_TX(UART_RX)
    );
    
    integer i0;
    integer i1;
    initial begin
        UART_START = 1'd0;
        UART_DIN = 8'h00;
        nRST = 1'd1;
        CLK_100MHz = 1'd0;
        UART_DATA_TO = 'd0;
        
        // --- Step #0: Reset
        #(3* WAIT_CLK_CYC);  nRST = 1'd0;
        repeat(2) begin
		  #(6* WAIT_CLK_CYC);  nRST = 1'b1;
		  #(6* WAIT_CLK_CYC);  nRST = 1'b0;
		end
		#(6* WAIT_CLK_CYC);  nRST = 1'b1;
		
		// --- Step #1: Read HEADER Information
        UART_DATA_TO <= {2'b11, 6'd0, 16'h0000};
        for (i1 = 'd0; i1 < FIFO_BYTE_SIZE; i1 = i1 + 'd1) begin
            #(WAIT_CYC_UART);   UART_DIN = UART_DATA_TO[(FIFO_BYTE_SIZE-i1)*'d8-'d1-:'d8];
                                UART_START = 1'd1;
            #(2*WAIT_CLK_CYC);  UART_START = 1'd0;
        end
        
        UART_DATA_TO <= {2'b11, 6'd1, 16'h0000};
        for (i1 = 'd0; i1 < FIFO_BYTE_SIZE; i1 = i1 + 'd1) begin
            #(WAIT_CYC_UART);   UART_DIN = UART_DATA_TO[(FIFO_BYTE_SIZE-i1)*'d8-'d1-:'d8];
                                UART_START = 1'd1;
            #(2*WAIT_CLK_CYC);  UART_START = 1'd0;
        end
        
        // --- Step #2: Enable System LED_TEST[0]
        UART_DATA_TO <= {2'b00, 6'd4, 16'h0001};
        for (i1 = 'd0; i1 < FIFO_BYTE_SIZE; i1 = i1 + 'd1) begin
            #(WAIT_CYC_UART);   UART_DIN = UART_DATA_TO[(FIFO_BYTE_SIZE-i1)*'d8-'d1-:'d8];
                                UART_START = 1'd1;
            #(2*WAIT_CLK_CYC);  UART_START = 1'd0;
        end
        
        // --- Step #3: Select DUT #3 (Waveform Calling) and get N samples
        UART_DATA_TO <= {2'b00, 6'd2, 16'h0003};
        for (i1 = 'd0; i1 < FIFO_BYTE_SIZE; i1 = i1 + 'd1) begin
            #(WAIT_CYC_UART);   UART_DIN = UART_DATA_TO[(FIFO_BYTE_SIZE-i1)*'d8-'d1-:'d8];
                                UART_START = 1'd1;
            #(2*WAIT_CLK_CYC);  UART_START = 1'd0;
        end
        
        for (i0 = 'd0; i0 < N_LUT_SIZE; i0 = i0 + 'd1) begin
            UART_DATA_TO <= {2'b00, 6'd1, 16'h0000};
            for (i1 = 'd0; i1 < FIFO_BYTE_SIZE; i1 = i1 + 'd1) begin
                #(WAIT_CYC_UART);   UART_DIN = UART_DATA_TO[(FIFO_BYTE_SIZE-i1)*'d8-'d1-:'d8];
                                    UART_START = 1'd1;
                #(2*WAIT_CLK_CYC);  UART_START = 1'd0;
            end
        end      
                
        // Step #4: Do echo test on DUT #0)
        UART_DATA_TO <= {2'b00, 5'd2, 16'h0000};
        for (i1 = 'd0; i1 < FIFO_BYTE_SIZE; i1 = i1 + 'd1) begin
            #(WAIT_CYC_UART);   UART_DIN = UART_DATA_TO[(FIFO_BYTE_SIZE-i1)*'d8-'d1-:'d8];
                                UART_START = 1'd1;
            #(2*WAIT_CLK_CYC);  UART_START = 1'd0;
        end
        for (i0 = 'd0; i0 < 'd202; i0 = i0 + 'd1) begin
            //Sending character for setting data 
            UART_DATA_TO[23:16] = {2'b00, 6'd1};
            UART_DATA_TO[15:0] = ('d1 << BIT_WIDTH -'d1) + ('d1 << BIT_WIDTH -'d1)* $sin(6.28* i0/'d101);
            
            for (i1 = 'd0; i1 < FIFO_BYTE_SIZE; i1 = i1 + 'd1) begin
                #(WAIT_CYC_UART);   UART_DIN = UART_DATA_TO[(FIFO_BYTE_SIZE-i1)*'d8-'d1-:'d8];
                                    UART_START = 1'd1;
                #(2*WAIT_CLK_CYC);  UART_START = 1'd0;
            end
        end
        
        // Step #5: Disable System LED_TEST[0]
        UART_DATA_TO <= {2'b00, 6'd0, 16'h0000};
        for (i1 = 'd0; i1 < FIFO_BYTE_SIZE; i1 = i1 + 'd1) begin
            #(WAIT_CYC_UART);   UART_DIN = UART_DATA_TO[(FIFO_BYTE_SIZE-i1)*'d8-'d1-:'d8];
                                UART_START = 1'd1;
            #(2*WAIT_CLK_CYC);  UART_START = 1'd0;
        end
        
        // Step #6: Ending
        #(4* WAIT_CYC_UART); $stop;
    end

endmodule
