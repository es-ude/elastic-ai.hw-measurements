# Framework for Hardware Characterization
This Python package provides APIs for handling the measurement devices within the IES laboratory incl. automated results analysis.
This is also part of the elastic AI ecosystem for deploying deep learning techniques on heterogeneous platform (MCU+FPGA/ASIC). 

## Using the package release in other Repos
Just adding this repo in the pyproject.toml file as dependencies by listing the git path. A detailed example is given in this [Python file](example/data_analysis.py).

## Installation
### Python for Developing
We recommended to install all python packages for using this API with a virtual environment (venv). Therefore, we also recommend to `uv` ([Link](https://docs.astral.sh/uv/)) package manager. `uv` is not a standard package installed on your OS. 
After installation, you can put-in ``uv sync`` into a terminal and the venv will be builded with installing all packages.

We also recommend to use ``devenv``.

## Structure
This repo includes two sub-packagges:
- Testing Verilog code on real FPGA ([Link to Readme](https://github.com/es-ude/elastic-ai.hw-measurements/elasticai/fpga_testing/README.md))
- Testing analog components of your system ([Link to Readme](https://github.com/es-ude/elastic-ai.hw-measurements/elasticai/hw_measurements/README.md))