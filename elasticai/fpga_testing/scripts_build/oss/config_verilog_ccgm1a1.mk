VLOG_SRC = $(shell find $(SRC_ROOT)/ -type f \( -iname "*.v" -o -iname "*.sv" \) ! -iname "*_tb.v")

# synthesize Verilog 
synth_vlog $(BUILD_OUT)/synth/$(TOP).json $(BUILD_OUT)/synth/$(TOP).v:
	mkdir -p $(BUILD_OUT)/synth
	yosys \
		-qql $(BUILD_OUT)/synth/$(TOP)_synth.log \
		-p 'read_verilog -sv $(VLOG_SRC); hierarchy -top $(TOP); synth_gatemate -top $(TOP) -luttree -nomx8; tee -o $(BUILD_OUT)/$(TOP)_util_sync.rpt stat -width; write_json $(BUILD_OUT)/synth/$(TOP).json; write_verilog $(BUILD_OUT)/synth/$(TOP).v'
# generate bitstream for FPGA
$(BUILD_OUT)/$(TOP).bin:
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
	gmpack $(BUILD_OUT)/impl/$(TOP).txt $(BUILD_OUT)/$(TOP).bit
