VLOG_SRC = $(shell find $(SRC_ROOT)/ -type f \( -iname "*.v" -o -iname "*.sv" \) ! -iname "*_tb.v")
CELLS_SYM := oss-cad-suite/share/yosys/gatemate/cells_sim.v
CPE_LIB := oss-cad-suite/share/yosys/gatemate/cells_bb.v

# synthesize Verilog 
.PHONY: synthesize
$(BUILD_OUT)/synth/$(TOP).json $(BUILD_OUT)/synth/$(TOP).v:
	mkdir -p $(BUILD_OUT)/synth
	yosys \
		-qql $(BUILD_OUT)/synth/$(TOP)_synth.log \
		-p 'read_verilog -sv $(VLOG_SRC); hierarchy -top $(TOP); synth_gatemate -top $(TOP) -luttree -nomx8; tee -o $(BUILD_OUT)/$(TOP)_util_sync.rpt stat -width; write_json $(BUILD_OUT)/synth/$(TOP).json; write_verilog $(BUILD_OUT)/synth/$(TOP).v'

# generate bitstream for FPGA
.PHONY: bitstream
$(BUILD_OUT)/$(TOP).bit: $(BUILD_OUT)/synth/$(TOP).json
	mkdir -p $(BUILD_OUT)/impl
	nextpnr-himbaechel \
	  --top $(TOP) \
		--device $(DEVICE) \
		--json $(BUILD_OUT)/synth/$(TOP).json \
		-o ccf=$(SRC_ROOT)/io.ccf \
		-o out=$(BUILD_OUT)/impl/$(TOP).txt \
		--router=router2 \
		--timing-allow-fail \
		--freq $(FREQ) \
	  2> $(BUILD_OUT)/$(TOP)_util_impl.rpt
	gmpack $(BUILD_OUT)/impl/$(TOP).txt $@

# generate simualtion for gtkwave 
.PHONY: simulation
$(BUILD_OUT)/sim/$(TOP).vcd: $(BUILD_OUT)/synth/$(TOP).json
	rm -rf $(BUILD_OUT)/sim/*
	mkdir -p $(BUILD_OUT)/sim
	iverilog -D'DUMPFILE="$(BUILD_OUT)/sim/$(TOP).vcd"' -o $(BUILD_OUT)/sim/$(TOP).vvp $(PRJ_ROOT)/$(SRC_DIR)/$(TOP).v $(SRC_ROOT)/$(TOP)_tb.v $(CELLS_SYM) $(CPE_LIB)
	vvp -n $(BUILD_OUT)/sim/$(TOP).vvp
