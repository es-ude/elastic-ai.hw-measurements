import os


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
