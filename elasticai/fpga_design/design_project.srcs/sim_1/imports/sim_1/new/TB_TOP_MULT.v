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


module TB_TOP_MULT();
    localparam FIFO_BYTE_SIZE = 'd3, BIT_WIDTH = 'd16, WAIT_CYC_UART = 'd100_000, WAIT_CLK_CYC = 'd5;
    localparam BITWIDTH_MULT = 'd8, N_MULT_INPUT = 8'd2;
    localparam DUT_SEL_NUM = 'd2;
    
    localparam MULT_VALUE0 = 'd40, MULT_VALUE1 = 'd41, MULT_OUT = MULT_VALUE0 * MULT_VALUE1;

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
    
    wire signed [N_MULT_INPUT* BITWIDTH_MULT-'d1:0] data_mult;
    assign data_mult = {MULT_VALUE1[BITWIDTH_MULT-'d1:0], MULT_VALUE0[BITWIDTH_MULT-'d1:0]}; 
    
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
    
    integer i0, i1;
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
         
        // --- Step #1: Select DUT
        UART_DATA_TO <= {2'b00, 6'd2, DUT_SEL_NUM[15:0]};
        for (i1 = 'd0; i1 < FIFO_BYTE_SIZE; i1 = i1 + 'd1) begin
            #(WAIT_CYC_UART);   UART_DIN = UART_DATA_TO[(FIFO_BYTE_SIZE-i1)*'d8-'d1-:'d8];
                                UART_START = 1'd1;
            #(2*WAIT_CLK_CYC);  UART_START = 1'd0;
        end
        
        // --- Step #2: Prepare Training with Writing data
        for (i0 = 'd0; i0 < ('d0 + N_MULT_INPUT); i0 = i0 + 'd1) begin
            UART_DATA_TO <= {2'b01, 6'd0+i0[5:0], data_mult[i0*BITWIDTH_MULT+:BITWIDTH_MULT], {{BIT_WIDTH-BITWIDTH_MULT}{1'd0}}};
            for (i1 = 'd0; i1 < FIFO_BYTE_SIZE; i1 = i1 + 'd1) begin
                #(WAIT_CYC_UART);   UART_DIN = UART_DATA_TO[(FIFO_BYTE_SIZE-i1)*'d8-'d1-:'d8];
                                    UART_START = 1'd1;
                #(2*WAIT_CLK_CYC);  UART_START = 1'd0;
            end
        end      
                
        // Step #3: Start Calculation
        for (i0 = 'd0; i0 < 'd2; i0 = i0 + 'd1) begin
            UART_DATA_TO <= {2'b00, 6'd1, 16'h0000};
            for (i1 = 'd0; i1 < FIFO_BYTE_SIZE; i1 = i1 + 'd1) begin
                #(WAIT_CYC_UART);   UART_DIN = UART_DATA_TO[(FIFO_BYTE_SIZE-i1)*'d8-'d1-:'d8];
                                    UART_START = 1'd1;
                #(2*WAIT_CLK_CYC);  UART_START = 1'd0;
            end
        end            
        
        // Step #4: Getting data
        repeat('d2) begin
            UART_DATA_TO <= {2'b00, 6'd0, 16'd0};
            for (i1 = 'd0; i1 < FIFO_BYTE_SIZE; i1 = i1 + 'd1) begin
                #(WAIT_CYC_UART);   UART_DIN = UART_DATA_TO[(FIFO_BYTE_SIZE-i1)*'d8-'d1-:'d8];
                                    UART_START = 1'd1;
                #(2*WAIT_CLK_CYC);  UART_START = 1'd0;
            end 
        end  
        
        // Step #5: Ending
        #(4* WAIT_CYC_UART); 
        $display("");
        $display("Multiplication of (%0d * %0d) is %0d (expected)", MULT_VALUE0[BITWIDTH_MULT-'d1:0], MULT_VALUE1[BITWIDTH_MULT-'d1:0], MULT_OUT[2*BITWIDTH_MULT-'d1:0]);
        $display("Accelerator answers with: %0d", UART_BACK_DATA['d15-:2*BITWIDTH_MULT]);
        $stop;
        
    end

endmodule
