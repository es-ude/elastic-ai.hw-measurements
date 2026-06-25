module TOP_MODULE(
	input wire CLK_10MHz,
	input wire RSTN,
	input wire BTTN,
	output wire LED
);
    // --- Using a PLL for enhancing system clock
    wire clk270, clk180, clk90, clk0, usr_ref_out;
    wire usr_pll_lock_stdy, usr_pll_lock;
    wire clk_sys;

    CC_PLL #(
        .REF_CLK("10.0"),  		// reference input in MHz
        .OUT_CLK("20.0"),    	// pll output frequency in MHz
        .PERF_MD("ECONOMY"), 	// LOWPOWER, ECONOMY, SPEED
        .LOW_JITTER(1),      	// 0: disable, 1: enable low jitter mode
        .CI_FILTER_CONST(2), 	// optional CI filter constant
        .CP_FILTER_CONST(4)  	// optional CP filter constant
    ) pll_inst (
        .CLK_REF(CLK_10MHz),
        .CLK_FEEDBACK(1'b0),
        .USR_CLK_REF(1'b0),
        .USR_LOCKED_STDY_RST(1'b0),
        .USR_PLL_LOCKED_STDY(usr_pll_lock_stdy),
        .USR_PLL_LOCKED(usr_pll_lock),
        .CLK270(clk270),
        .CLK180(clk180),
        .CLK90(clk90),
        .CLK0(clk0),
        .CLK_REF_OUT(usr_ref_out)
    );
    assign clk_sys = clk0;

    // --- Implementing user logic
    reg [20:0] counter;
    always@(posedge clk0)	begin
        if (~RSTN) begin
            counter <= 0;
        end else begin
            counter <= counter + 'd1;
        end
    end
    assign LED = counter[20];
endmodule
