VLOG_SRC = $(shell find $(SRC_ROOT)/ -type f \( -iname "*.v" -o -iname "*.sv" \) ! -iname "*_tb.v")
CELLS_SYM := oss-cad-suite/share/yosys/ice40/cell_sim.v

# synthesize Verilog 
.PHONY: synthesize
synth_vlog $(BUILD_OUT)/synth/$(TOP).json:
	mkdir -p $(BUILD_OUT)/synth
	yosys \
	    -qql $(BUILD_OUT)/synth/$(TOP).log \
	    -p 'read_verilog -sv $(VLOG_SRC); hierarchy -top $(TOP); synth_ice40 -top $(TOP); tee -o $(BUILD_OUT)/$(TOP)_util_sync.rpt stat -width; write_json $@; write_verilog $(BUILD_OUT)/synth/$(TOP).v;'

# implementation
.PHONY: bitstream
$(BUILD_OUT)/$(TOP).bit: $(BUILD_OUT)/synth/$(TOP).json
	mkdir -p $(PRJ_ROOT)/$(BUILD_OUT)/impl
	nextpnr-ice40 \
		--up5k \
		--package $(PACKAGE) \
		--json $< \
		--pcf $(SRC_ROOT)/io.pcf \
		--asc $(BUILD_OUT)/impl/$(TOP).asc \
		--timing-allow-fail \
		--freq $(FREQ) \
		2> $(BUILD_OUT)/$(TOP)_util_impl.rpt
	icetime \
		-d up5k \
		-P $(PACKAGE) \
		-c $(FREQ) \
		-p $(SRC_ROOT)/io.pcf \
		-r $(BUILD_OUT)/$(TOP)_timing.rpt \
		$(BUILD_OUT)/impl/$(TOP).asc
	icepack $(BUILD_OUT)/impl/$(TOP).asc $@

# generate simualtion for gtkwave 
.PHONY: simulation
$(BUILD_OUT)/sim/$(TOP).vcd: $(BUILD_OUT)/synth/$(TOP).json
	rm -rf $(BUILD_OUT)/sim/*
	mkdir -p $(BUILD_OUT)/sim
	iverilog -D'DUMPFILE="$(BUILD_OUT)/sim/$(TOP).vcd"' -o $(BUILD_OUT)/sim/$(TOP).vvp $(PRJ_ROOT)/$(SRC_DIR)/$(TOP).v $(SRC_ROOT)/$(TOP)_tb.v $(CELLS_SYM)
	vvp -n $(BUILD_OUT)/sim/$(TOP).vvp
