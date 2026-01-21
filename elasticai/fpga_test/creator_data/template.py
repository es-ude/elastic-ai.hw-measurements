import numpy as np
from elasticai.creator.nn.fixed_point import Linear
from torch import nn, ones_like, Tensor, cat, zeros
from elasticai.creator_plugins.test_env.src.fixedpoint_handler import FixedPointConfig


def get_basic_test_model(num_inputs: int, num_outputs: int, total_bits: int, frac_bits: int) -> nn.Sequential:
    model = nn.Sequential(
        Linear(
            in_features=num_inputs,
            out_features=num_outputs,
            bias=True,
            total_bits=total_bits,
            frac_bits=frac_bits,
        )
    )
    model[0].weight.data = ones_like(model[0].weight) * 2
    model[0].bias.data = Tensor([-1.0, 1.0, 2.0])
    return model


def get_basic_data_model(num_input: int, bit_width: int, frac_width: int, signed_data: bool, inc_value=0.25) -> Tensor:
    max_val = (2**(bit_width - frac_width))
    start_value = -max_val/2 if signed_data else 0
    stop_value = max_val/2 if signed_data else max_val

    # Creating the dummy
    input_tensor = zeros((1, num_input))
    for idx_array in range(0, num_input):
        for value in np.arange(start_value, stop_value, inc_value):
            list_zeros = [0.0 for idx in range(0, num_input)]
            list_zeros[idx_array] = value

            new_input = Tensor([list_zeros])
            input_tensor = cat(
                (input_tensor, new_input), dim=0
            )

    # Converting to fixed point
    fxp_conf = FixedPointConfig(bit_width, frac_width)
    return fxp_conf.as_rational(fxp_conf.as_integer(input_tensor))


if __name__ == "__main__":
    data = get_basic_data_model(
        num_input=5,
        bit_width=8,
        frac_width=6,
        signed_data=True,
        inc_value=0.125
    )
    print(data)
