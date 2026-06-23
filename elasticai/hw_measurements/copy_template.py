from pathlib import Path
from shutil import copy

import elasticai.hw_measurements as temp


def copy_characterization_template(type: str, path2save: Path) -> None:
    """Copying the template to handle a characterization measurement
    :param type:        Type of measurement ["adc", "amp", "dac", "noise"]
    :param path2save:   Path to generate the files
    :return:            None
    """
    types_avai = ["adc", "amp", "dac", "noise"]
    if type.lower() not in types_avai:
        raise ValueError(f"Not available template - Only {types_avai}")

    path2temp = Path(temp.__file__).parent / "template"
    path2file = path2temp / f"{type.lower()}.py"

    path2save.mkdir(parents=True, exist_ok=True)
    copy(
        src=path2file,
        dst=path2save / f"{type.lower()}.py",
    )
