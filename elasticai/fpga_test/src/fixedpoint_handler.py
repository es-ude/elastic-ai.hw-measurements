from dataclasses import dataclass
from torch import Tensor, flatten
from typing import Protocol, TypeVar, Union, cast, overload, runtime_checkable

T = TypeVar("T", bound="ConvertableToFixedPointValues")


@runtime_checkable
class ConvertableToFixedPointValues(Protocol[T]):
    def round(self: T) -> T: ...

    def int(self: T) -> T: ...

    def float(self: T) -> T: ...

    def __gt__(self: T, other: Union[int, float, T]) -> T:  # type: ignore
        ...

    def __lt__(self: T, other: Union[int, float, T]) -> T:  # type: ignore
        ...

    def __or__(self: T, other: T) -> T: ...

    def __mul__(self: T, other: Union[int, T, float]) -> T:  # type: ignore
        ...

    def __truediv__(self: T, other: Union[int, float]) -> T:  # type: ignore
        ...


@dataclass
class FixedPointConfig:
    total_bits: int
    frac_bits: int

    @property
    def minimum_as_integer(self) -> int:
        return 2 ** (self.total_bits - 1) * (-1)

    @property
    def maximum_as_integer(self) -> int:
        return 2 ** (self.total_bits - 1) - 1

    @property
    def minimum_as_rational(self) -> float:
        return -1 * (1 << (self.total_bits - 1)) / (1 << self.frac_bits)

    @property
    def maximum_as_rational(self) -> float:
        return int("1" * (self.total_bits - 1), 2) / (1 << self.frac_bits)

    def integer_out_of_bounds(self, number: T) -> T:
        return (number < self.minimum_as_integer) | (number > self.maximum_as_integer)

    def rational_out_of_bounds(self, number: T) -> T:
        return (number < self.minimum_as_rational) | (number > self.maximum_as_rational)

    @overload
    def as_integer(self, number: float | int) -> int: ...

    @overload
    def as_integer(self, number: T) -> T: ...

    def as_integer(self, number: float | int | T) -> int | T:
        if isinstance(number, ConvertableToFixedPointValues):
            return self._convert_T_to_integer(cast(T, number))
        return self._convert_float_or_int_to_integer(number)

    @overload
    def as_rational(self, number: float | int) -> float: ...

    @overload
    def as_rational(self, number: T) -> T: ...

    def as_rational(self, number: float | int | T) -> float | T:
        return number / (1 << self.frac_bits)

    def _convert_T_to_integer(self, number: T) -> T:
        return (number * (1 << self.frac_bits)).int().float()

    def _convert_float_or_int_to_integer(self, number: float | int) -> int:
        return round(number * (1 << self.frac_bits))


def parse_fxp_tensor_to_bytearray(
    tensor: Tensor, total_bits: int, frac_bits: int
) -> list[bytearray]:
    tensor = flatten(tensor.permute([0, 2, 1]), start_dim=1)
    fxp_config = FixedPointConfig(total_bits=total_bits, frac_bits=frac_bits)
    ints = fxp_config.as_integer(tensor).tolist()
    data = list()
    for i, batch in enumerate(ints):
        data.append(bytearray())
        for item in batch:
            item_as_bytes = int(item).to_bytes(1, byteorder="big", signed=True)
            data[i].extend(item_as_bytes)
    return data


def parse_bytearray_to_fxp_tensor(
    data: list[bytearray], total_bits: int, frac_bits: int, dimensions: tuple
) -> Tensor:
    fxp_config = FixedPointConfig(total_bits=total_bits, frac_bits=frac_bits)
    rationals = list()
    for i, batch in enumerate(data):
        rationals.append(list())
        my_batch = batch.hex(sep=" ", bytes_per_sep=1).split(" ")
        for item in my_batch:
            item_as_bytes = bytes.fromhex(item)
            item_as_int = int.from_bytes(item_as_bytes, byteorder="big", signed=True)
            item_as_rational = fxp_config.as_rational(item_as_int)
            rationals[i].append(item_as_rational)
    tensor = Tensor(rationals)
    tensor = tensor.unflatten(1, (dimensions[2], dimensions[1]))
    tensor = tensor.transpose(1, 2)
    return tensor
