VLOG_SRC = $(shell find $(PRJ_ROOT)/$(SRC_DIR)/ -type f \( -iname \*.v -o -iname \*.sv \))

ifeq ($(DEVICE),UP5K)
# synthesize Verilog 
$(BUILD_OUT)/synth/$(TOP).json: $(VLOG_SRC)
	rm -rf $(BUILD_OUT)
	mkdir -p $(BUILD_OUT)/synth
	yosys \
	-qql $(BUILD_OUT)/synth/$(TOP).log \
	-p 'read_verilog -sv $^; hierarchy -top $(TOP); synth_ice40 -top $(TOP); tee -o $(BUILD_OUT)/$(TOP)_util_sync.rpt stat -width; write_json $@; write_verilog $(BUILD_OUT)/synth/$(TOP)_mapped.v;'
# implementation
$(BUILD_OUT)/$(TOP).bin: $(BUILD_OUT)/synth/$(TOP).json
	mkdir -p $(PRJ_ROOT)/$(BUILD_OUT)/impl
	nextpnr-ice40 \
		--up5k \
		--package $(PACKAGE) \
		--json $< \
		--pcf $(PRJ_ROOT)/$(SRC_DIR)/io.pcf \
		--asc $(BUILD_OUT)/impl/$(TOP).asc \
		--timing-allow-fail \
		--freq $(FREQ) \
		2> $(BUILD_OUT)/$(TOP)_util_impl.rpt
	icetime \
		-d up5k \
		-P $(PACKAGE) \
		-c $(FREQ) \
		-p src/io.pcf \
		-r $(BUILD_OUT)/$(TOP)_timing.rpt \
		$(BUILD_OUT)/impl/$(TOP).asc
	icepack $(BUILD_OUT)/impl/$(TOP).asc $@
else ifeq ($(DEVICE),CCGM1A1)
# synthesize Verilog 
synth_vlog $(BUILD_OUT)/synth/$(TOP).json $(BUILD_OUT)/synth/$(TOP).v: $(VLOG_SRC)
	rm -rf $(BUILD_OUT)
	mkdir -p $(BUILD_OUT)/synth
	yosys \
		-qql $(BUILD_OUT)/synth/$(TOP)_synth.log \
		-p 'read_verilog -sv $^; synth_gatemate -top $(TOP) -luttree -nomx8; write_json $(BUILD_OUT)/synth/$(TOP).json; write_verilog $(BUILD_OUT)/synth/$(TOP).v'
# generate bitstream for FPGA
$(BUILD_OUT)/$(TOP).bin: $(BUILD_OUT)/synth/$(TOP).json
	mkdir -p $(BUILD_OUT)/impl
	nextpnr-himbaechel \
		--device $(DEVICE) \
		--json $(BUILD_OUT)/synth/$(TOP).json \
		-o ccf=$(PRJ_ROOT)/$(SRC_DIR)/io.ccf \
		-o out=$(BUILD_OUT)/impl/$(TOP).txt \
		--router=router2 \
		--timing-allow-fail \
		--freq $(FREQ)
	gmpack $(BUILD_OUT)/impl/$(TOP).txt $(BUILD_OUT)/$(TOP).bit
else
	$(error Unsupported device: $(DEVICE))
endif