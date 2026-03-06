`timescale 1 ns / 1 ps

module TOP_MODULE_TB;
	reg clk;
	reg rst;
	wire led;

    // Clock generation
	always clk = #100 ~clk;

	// DUT including
	TOP_MODULE DUT (
		.CLK_10MHz(clk),
		.RSTN(rst),
		.BTTN(1'd0),
		.LED(led)
	);

    // Test procotol
	initial begin
        `ifdef CCSDF
		    $sdf_annotate("blink_00.sdf", DUT);
        `endif
		$dumpfile("build/sim/top_module.vcd");
		$dumpvars(0, TOP_MODULE_TB);

		clk = 0;
		rst = 0;

		#200;
		rst = 1;
		#500;
		$finish;
	end
endmodule
