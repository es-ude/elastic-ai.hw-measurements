# Example: Noise

This example shows how to use `extract_noise_metrics` to process a transient
noise measurement: extracting noise metrics, computing the noise power
spectrum, removing power-line noise, and plotting the results.

## Source Code

```{literalinclude} ../../elasticai/hw_measurements/template/noise.py
:language: python
:linenos:
```

## Workflow

1. A `CharacterizationNoise` instance is created and loaded with the
   transient measurement data (timestamps, raw signal, and channels).
2. `extract_transient_metrics()` computes basic transient metrics such as
   the channel offset mean.
3. `extract_noise_power_distribution()` computes the noise power
   distribution, scaling the digital values with `scale_adc` and splitting
   the signal into `num_segments` segments.
4. `exclude_channels_from_spec()` removes the specified channels from the
   spectral analysis.
5. `remove_power_line_noise()` filters out power-line noise and its
   harmonics from the spectrum, within a given tolerance.
6. `extract_noise_rms()` computes the RMS noise value.
7. The transient signal and the noise spectrum are plotted via
   `plot_transient_noise()` and `plot_spectrum_noise()`, with plots saved
   next to the input file.

## Minimal Example

```{code-block} python
:linenos:

from pathlib import Path

dut = extract_noise_metrics(
    data=transient_data,
    exclude_channels=[],