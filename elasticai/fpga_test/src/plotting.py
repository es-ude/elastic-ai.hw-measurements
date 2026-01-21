import os
import numpy as np
import matplotlib.pyplot as plt


def get_color_plot(idx: int) -> str:
    """Getting the color ID for plotting"""
    color = 'krbg'
    return color[idx % 4]


def save_figure(fig, path: str, name: str, format: list=['jpg','svg']) -> None:
    """Function for saving the figure in specific format
    Args:
        fig:        Matplotlib Figure for saving
        path:       Path to save the figure
        name:       Name of the saved figure
        format:     Format for saving the figures
    """
    path2fig = os.path.join(path, name)
    for idx, form in enumerate(format):
        file_name = path2fig + '.' + form
        fig.savefig(file_name, format=form)


def plot_transient(t0: np.ndarray, xin: np.ndarray, xout: np.ndarray, path: str='', fsig: float=0.0, block_plot: bool=False, is_echo_test: bool=False) -> None:
    """Plotting the transient signals
    Args:
        t0:             Numpy array with transient timestamp
        xin:            Numpy array with transient signal which is transferred to device
        xout:           Numpy array with transient signal which returns from device
        path:           Path for saving the results
        fsig:           Signal frequency
        block_plot:     Blocking and showing plot
        is_echo_test:   Echo test
    Returns:
        None
    """
    plt.figure()

    if fsig:
        xpos0 = np.argwhere(t0 >= 1/fsig).flatten()[0]
        xpos1 = np.argwhere(t0 >= 5/fsig).flatten()[0]

        plt.plot(t0[xpos0:xpos1], xin[xpos0:xpos1], marker='.', markersize=4, color=get_color_plot(0), label='Input')
        plt.plot(t0[xpos0:xpos1], xout[xpos0:xpos1], marker='.', markersize=4, color=get_color_plot(1), label='Output')
    else:
        plt.plot(t0, xin, marker='.', markersize=4, color=get_color_plot(0), label='Input')
        plt.plot(t0, xout, marker='.', markersize=4, color=get_color_plot(1), label='Output')

    plt.xlabel('Time / s')
    plt.ylabel('X_y')
    if is_echo_test:
        plt.title(f'MAE of Echo Test: {np.sum(np.abs(xin - xout))}')
    plt.legend(loc='upper left')

    plt.grid()
    plt.tight_layout(pad=0.5)
    if path:
        save_figure(plt, path, f'transient_{int(fsig)}Hz')
    if block_plot:
        plt.show(block=True)


def plot_call(xout: np.ndarray, path: str='', block_plot: bool=False) -> None:
    """Plotting the signals from calling the DUT
    Args:
        xout:           Numpy array with transient signal which returns from device
        path:           Path for saving the results
        block_plot:     Blocking and showing plot
    Returns:
        None
    """
    plt.figure()
    plt.plot(xout, marker='.', markersize=4, color=get_color_plot(0), label='Output')

    plt.xlim([0, xout.size])
    plt.xlabel('Call Iteration')
    plt.ylabel(r'X_${out}$')

    plt.grid()
    plt.tight_layout(pad=0.5)
    if path:
        save_figure(plt, path, f'call_lut')
    if block_plot:
        plt.show(block=True)


def plot_bode(f_sig: np.ndarray, data_dut: dict, path: str='', block_plot: bool=False) -> None:
    """Plotting the bode diagram of selected device under test
    Args:
        f_sig:          Numpy array with signal frequencies
        data_dut:       Dictionary with results
        path:           Path for saving the figure
        block_plot:     Blocking and showing plot
    Return:
        None
    """
    gain_dut = np.array(data_dut['gain_dut'])
    phase_dut = np.array(data_dut['phase_dut'])

    # --- Configure plot
    plt.figure()
    ax0 = plt.subplot(211)
    ax1 = plt.subplot(212)

    # --- Plot: DUT
    ax0.semilogx(f_sig, gain_dut, marker='.', markersize=4, color=get_color_plot(0), label="DUT")
    ax0.set_ylabel('Gain (dB)')
    ax0.grid(True)

    ax1.semilogx(f_sig, phase_dut, marker='.', markersize=4, color=get_color_plot(0))
    ax1.set_ylabel('Phase (°)')
    ax1.set_xlabel('Sampling frequency f_s (Hz)')
    ax1.grid(True)

    ax1.set_ylim(-180, 180)
    ax1.set_yticks(range(-180, 180, 45))

    # --- Plot: EMU
    ax0.semilogx(f_sig, 20*np.log10(data_dut['gain_emu']), marker='.', markersize=4, color=get_color_plot(1), label="Emulation")
    ax1.semilogx(f_sig, data_dut['phase_emu'], marker='.', markersize=4, color=get_color_plot(1))

    ax0.legend()
    plt.tight_layout(pad=0.5)
    if path:
        save_figure(plt, path, 'bode_plot')
    if block_plot:
        plt.show(block=True)


def plot_arithmetic(data_out: np.ndarray, data_ref: np.ndarray,
                    path2save: str='', block_plot: bool=False) -> None:
    """Function for plotting the arithmetic test results
    :param data_out:    Numpy array with output values
    :param data_ref:    Numpy array with reference values
    :param path2save:   Path for saving the results
    :param block_plot:  Blocking and showing plot
    :return:            None
    """
    plt.figure()
    plt.plot(data_ref, data_out, marker='.', linestyle='None', color=get_color_plot(0))
    plt.xlabel(r'Digital Input $x$')
    plt.ylabel(r'Digital Output $y$')

    mae = np.sum(np.abs(data_ref - data_out)) / data_ref.size
    plt.title(f'MAE = {mae:.4f}')

    plt.grid(True)
    plt.tight_layout(pad=0.5)
    if path2save:
        save_figure(plt, path2save, 'arith_test')
    if block_plot:
        plt.show(block=True)
