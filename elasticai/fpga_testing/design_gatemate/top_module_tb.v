`timescale 1 ns / 1 ps

`ifndef DUMPFILE
`define DUMPFILE "build/sim/TOP_MODULE.vcd"
`endif

module TOP_MODULE_TB;
  reg  clk;
  reg  rst;
  wire led;

  // Clock generation
  always #100 clk <= ~clk;

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
    $dumpfile(`DUMPFILE);
    $dumpvars(0, TOP_MODULE_TB);

    clk = 0;
    rst = 0;

    #200;
    rst = 1;
    #500;

    $stop;
  end
endmodule
