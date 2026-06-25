# Framework for Hardware Characterization 
This Python package provides APIs for testing Verilog code on FPGAs. This repo includes templates for different devices and Python code in order to test them.
This is also part of the elasticAI ecosystem for deploying deep learning techniques on heterogeneous platform (MCU+FPGA/ASIC). 


## Installation - Third-Party Code
For generating the bitstream for the FPGAs (actual only ChipCologne GateMate A1 and Lattice ICE40UP5K are supported), the OSS-CAD suite is used. After initialization and starting ``devenv``, the env checks, if it is installed. It not, you will get the information.


## Building FPGA designs for testing
We will provide a basic structure for testing FPGA designs on
1. Digilent Arty-A7 boards ([Link](https://digilent.com/reference/programmable-logic/arty-a7/start?srsltid=AfmBOoqeya_KoM1qKi6M-j7AMEs77-xNVkFL-W1l7ACA632gUgNiiGkL))
2. UDE-IES elasticAI.hardware V5 ([Link](https://github.com/es-ude/elastic-ai.hardware/tree/master/v5/revision_2))
3. Olimex GateMateA1-EVB ([Link](https://github.com/OLIMEX/GateMateA1-EVB/tree/main))