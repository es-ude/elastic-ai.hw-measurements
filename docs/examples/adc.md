# Example: ADC

This example shows how to use `TestHandlerADC` to run an ADC characterization
on the DUT: connecting to the DUT and the lab power supply, running the
transfer test, saving the results, and plotting them.

## Source Code

```{literalinclude} ../../elasticai/hw_measurements/template/adc.py
:language: python
:linenos:
```

## Workflow

1. `TestHandlerADC` is initialized with the DUT's COM port and, optionally,
   the lab equipment's COM ports.
2. In the constructor, unless debug or plot-only mode is enabled, the
   connection to the NGU-X01 power supply is established and a beep confirms
   the connection.
3. `run_transfer_test()` activates the output, runs the ADC transfer test,
   and saves the results as an `.npz` file in the `runs` folder.
4. `plot_results_from_measurement()` or `plot_results_from_file()` visualize
   the measurement results.

## Minimal Example

```{code-block} python
:linenos:

hndl = TestHandlerADC(com_dut='COM7', en_debug=False, only_plot=False)
data = hndl.run_transfer_test()
hndl.plot_results_from_measurement(data)
```