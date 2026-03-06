PRJ_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/../..)
SRC_ROOT := $(PRJ_ROOT)/$(SRC_DIR)
TMP_ROOT := $(PRJ_ROOT)/scripts_build/oss
BUILD_OUT := build

.PHONY: all
all: flash

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
    include $(TMP_ROOT)/config_verilog_up5k.mk
else ifeq ($(DEVICE),CCGM1A1)
    include $(TMP_ROOT)/config_verilog_ccgm1a1.mk
else
	$(error Unsupported device: $(DEVICE))
endif
