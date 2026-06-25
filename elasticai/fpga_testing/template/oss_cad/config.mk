PRJ_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
SRC_ROOT := $(PRJ_ROOT)/$(SRC_DIR)
SCRIPTS_ROOT := $(PRJ_ROOT)/scripts
BUILD_OUT := $(PRJ_ROOT)/build


print-paths:
	@echo "PRJ_ROOT  = $(PRJ_ROOT)"
	@echo "SRC_ROOT  = $(SRC_ROOT)"
	@echo "SCRIPTS_ROOT  = $(SCRIPTS_ROOT)"
	@echo "BUILD_OUT = $(BUILD_OUT)"


.PHONY: all
all: clean synthesize bitstream

.PHONY: synthesize
synthesize: $(BUILD_OUT)/synth/$(TOP).json

.PHONY: bitstream
bitstream: $(BUILD_OUT)/$(TOP).bin

.PHONY: wave
wave: $(BUILD_OUT)/sim/$(TOP).vcd
	gtkwave $(BUILD_OUT)/sim/$(TOP).vcd

.PHONY: flash
flash: $(BUILD_OUT)/$(TOP).bit
	openFPGALoader --cable dirtyJtag --reset --bitstream $(BUILD_OUT)/$(TOP).bit

.PHONY: clean
clean:
	rm -rf $(BUILD_OUT)/*

##################################################
## File Generation
ifeq ($(DEVICE),UP5K)
    include $(SCRIPTS_ROOT)/config_verilog_up5k.mk
else ifeq ($(DEVICE),CCGM1A1)
    include $(SCRIPTS_ROOT)/config_verilog_ccgm1a1.mk
else
	$(error Unsupported device: $(DEVICE))
endif
