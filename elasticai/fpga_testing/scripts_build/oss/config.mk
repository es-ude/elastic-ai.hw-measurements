PRJ_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/../..)
BUILD_OUT := build
CELLS_SYM := oss-cad-suite/share/yosys/gatemate/cells_sim.v
CPE_LIB := $(PRJ_ROOT)/scripts_build/gatemate/cpelib.v

.PHONY: all
all: clean synthesize bitstream

.PHONY: synthesize
synthesize: $(BUILD_OUT)/synth/$(TOP).json

.PHONY: bitstream
bitstream: $(BUILD_OUT)/$(TOP).bin

.PHONY: simulation
simulation:
	rm -rf $(BUILD_OUT)/sim/*
	mkdir -p $(BUILD_OUT)/sim
	iverilog -o $(BUILD_OUT)/sim/$(TOP).vvp $(PRJ_ROOT)/$(SRC_DIR)/$(TOP).v $(PRJ_ROOT)/$(SRC_DIR)/$(TOP)_tb.v $(CELLS_SYM) $(CPE_LIB)
	vvp -N $(BUILD_OUT)/sim/$(TOP).vvp

.PHONY: wave
wave:
	$(BUILD_OUT)/sim/$(TOP).vcd
	gtkwave $(BUILD_OUT)/sim/$(TOP).vcd

.PHONY: flash
flash:
	$(BUILD_OUT)/$(TOP).bit
	openFPGALoader --cable dirtyJtag --reset --bitstream $(BUILD_OUT)/$(TOP).bin

.PHONY: clean
clean:
	rm -rf $(BUILD_OUT)/*

##################################################
## File Generation
include $(PRJ_ROOT)/scripts_build/oss/config_verilog.mk
