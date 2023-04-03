from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class BidOrderMapJSON(typing.TypedDict):
    kind: typing.Literal["BidOrderMap"]


class AskOrderMapJSON(typing.TypedDict):
    kind: typing.Literal["AskOrderMap"]


class BidOrderJSON(typing.TypedDict):
    kind: typing.Literal["BidOrder"]


class AskOrderJSON(typing.TypedDict):
    kind: typing.Literal["AskOrder"]


@dataclass
class BidOrderMap:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "BidOrderMap"

    @classmethod
    def to_json(cls) -> BidOrderMapJSON:
        return BidOrderMapJSON(
            kind="BidOrderMap",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "BidOrderMap": {},
        }


@dataclass
class AskOrderMap:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "AskOrderMap"

    @classmethod
    def to_json(cls) -> AskOrderMapJSON:
        return AskOrderMapJSON(
            kind="AskOrderMap",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AskOrderMap": {},
        }


@dataclass
class BidOrder:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "BidOrder"

    @classmethod
    def to_json(cls) -> BidOrderJSON:
        return BidOrderJSON(
            kind="BidOrder",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "BidOrder": {},
        }


@dataclass
class AskOrder:
    discriminator: typing.ClassVar = 3
    kind: typing.ClassVar = "AskOrder"

    @classmethod
    def to_json(cls) -> AskOrderJSON:
        return AskOrderJSON(
            kind="AskOrder",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AskOrder": {},
        }


OrderDTKind = typing.Union[BidOrderMap, AskOrderMap, BidOrder, AskOrder]
OrderDTJSON = typing.Union[BidOrderMapJSON, AskOrderMapJSON, BidOrderJSON, AskOrderJSON]


def from_decoded(obj: dict) -> OrderDTKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "BidOrderMap" in obj:
        return BidOrderMap()
    if "AskOrderMap" in obj:
        return AskOrderMap()
    if "BidOrder" in obj:
        return BidOrder()
    if "AskOrder" in obj:
        return AskOrder()
    raise ValueError("Invalid enum object")


def from_json(obj: OrderDTJSON) -> OrderDTKind:
    if obj["kind"] == "BidOrderMap":
        return BidOrderMap()
    if obj["kind"] == "AskOrderMap":
        return AskOrderMap()
    if obj["kind"] == "BidOrder":
        return BidOrder()
    if obj["kind"] == "AskOrder":
        return AskOrder()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "BidOrderMap" / borsh.CStruct(),
    "AskOrderMap" / borsh.CStruct(),
    "BidOrder" / borsh.CStruct(),
    "AskOrder" / borsh.CStruct(),
)
