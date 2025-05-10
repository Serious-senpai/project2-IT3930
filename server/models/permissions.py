from __future__ import annotations

from typing import Callable, Type, TYPE_CHECKING


__all__ = ("Permission",)


class flag_value:

    __slots__ = ("flag",)
    if TYPE_CHECKING:
        flag: Callable[[Permission], int]

    def __init__(self, flag: Callable[[Permission], int]) -> None:
        self.flag = flag

    def __get__(self, o: Permission, _: Type[Permission]) -> bool:
        return bool(o.value & self.flag(o))


class Permission:

    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value = value

    @flag_value
    def administrator(self) -> int:
        return 1 << 0

    @flag_value
    def view_users(self) -> int:
        return 1 << 1

    @flag_value
    def create_violation(self) -> int:
        return 1 << 2
