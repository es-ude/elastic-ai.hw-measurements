# Example: Amplifier

This example shows how to use `TestHandlerAmplifier` to characterize an
electronic amplifier stage: connecting to the lab power supply and DMM,
running the transfer test on a given channel, saving the results, and
plotting them.

## Source Code

```{literalinclude} ../../elasticai/hw_measurements/template/amp.py
:language: python
:linenos:
```

## Workflow

1. `TestHandlerAmplifier` is initialized, optionally with the lab equipment's
   COM ports.
2. Unless debug or plot-only mode is enabled, the constructor opens a
   connection to the NGU-X01 power supply and the DMM6500 multimeter, each
   confirmed with a beep.
3. `run_transfer_test(chnnl_num)` activates the source output, runs the
   amplifier transfer test on the specified channel, and saves the results
   as an `.npz` file in the `runs` folder.
4. `plot_results_from_measurement()` or `plot_results_from_file()` visualize
   the measurement results.

## Minimal Example

```{code-block} python
:linenos:

hndl = TestHandlerAmplifier(en_debug=False, only_plot=False)
data = hndl.run_transfer_test(0)
hndl.plot_results_from_measurement(data)
```