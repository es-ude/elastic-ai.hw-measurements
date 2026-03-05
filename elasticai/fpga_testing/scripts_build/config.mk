PRJ_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
BUILD_OUT := build

.PHONY: all
all: clean bitstream

.PHONY: synthesize
synthesize: $(BUILD_OUT)/synth/$(TOP).json

.PHONY: bitstream
bitstream: $(BUILD_OUT)/$(TOP).bin

.PHONY: wave
wave: $(BUILD_OUT)/sim/$(TOP).vcd
	$(GTKW) $(BUILD_OUT)/sim/$(TOP).vcd

.PHONY: flash
flash: $(BUILD_OUT)/$(TOP).bit
	openFPGALoader --cable dirtyJtag --reset --bitstream $(BUILD_OUT)/$(TOP).bin

.PHONY: clean
clean:
	rm -rf $(BUILD_OUT)/*
	mkdir -p $(BUILD_OUT)

##################################################
## File Generation
include $(PRJ_ROOT)/scripts_build/config_verilog.mk

##################################################
## Simulation
IVL ?= iverilog
VVP ?= vvp
GTKW ?= gtkwave

CELLS_SYM ?= oss-cad-suite/share/yosys/gatemate/cells_sim.v
IVLFLAGS ?= -g2012 -gspecify -Ttyp

sim/$(TOP).vvp: $(BUILD_OUT)/synth/$(TOP).v
	$(IVL) -o $(BUILD_OUT)/sim/$(TOP).vvp $(BUILD_OUT)/synth/$(TOP).v $(SRC_DIR)/$(TOP)_tb.v $(CELLS_SYM) sim/cpelib.v

sim/$(TOP).vcd: $(BUILD_OUT)/sim/$(TOP).vvp
	$(VVP) -N $(BUILD_OUT)/sim/$(TOP).vvp

