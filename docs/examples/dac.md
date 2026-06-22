# DAC Characterization – Example

This example shows how to use `TestHandlerDAC` to characterize a
Digital-Analog-Converter on the DUT: connecting to the DUT and the DMM,
running the transfer test, saving the results, and plotting them.

## Source Code

```{literalinclude} ../../elasticai/hw_measurements/template/dac.py
:language: python
:linenos:
```

## Workflow

1. `TestHandlerDAC` is initialized with the DUT's COM port and, optionally,
   the lab equipment's COM ports.
2. Unless plot-only mode is enabled, a connection to the DUT is established.
3. Unless debug or plot-only mode is enabled, the constructor also opens a
   connection to the DMM6500 multimeter, confirmed with a beep.
4. `run_transfer_test(get_voltage)` runs the DAC transfer test, reading
   either voltage or current from the DMM depending on the `get_voltage`
   flag, and saves the results as an `.npz` file in the `runs` folder.
5. `plot_results_from_measurement()` or `plot_results_from_file()` visualize
   the measurement results.

## Minimal Example

```{code-block} python
:linenos:

hndl = TestHandlerDAC(com_dut='COM7', en_debug=False, only_plot=False)
data = hndl.run_transfer_test(get_voltage=True)
hndl.plot_results_from_measurement(data)
```