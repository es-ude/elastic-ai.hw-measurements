VLOG_SRC = $(shell find $(SRC_ROOT)/ -type f \( -iname "*.v" -o -iname "*.sv" \) ! -iname "*_tb.v")

# synthesize Verilog 
$(BUILD_OUT)/synth/$(TOP).json:
	mkdir -p $(BUILD_OUT)/synth
	yosys \
	    -qql $(BUILD_OUT)/synth/$(TOP).log \
	    -p 'read_verilog -sv $(VLOG_SRC); hierarchy -top $(TOP); synth_ice40 -top $(TOP); tee -o $(BUILD_OUT)/$(TOP)_util_sync.rpt stat -width; write_json $@; write_verilog $(BUILD_OUT)/synth/$(TOP).v;'
# implementation
$(BUILD_OUT)/$(TOP).bin:
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
