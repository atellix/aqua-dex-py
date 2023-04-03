from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class AccountMapJSON(typing.TypedDict):
    kind: typing.Literal["AccountMap"]


class AccountJSON(typing.TypedDict):
    kind: typing.Literal["Account"]


@dataclass
class AccountMap:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "AccountMap"

    @classmethod
    def to_json(cls) -> AccountMapJSON:
        return AccountMapJSON(
            kind="AccountMap",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AccountMap": {},
        }


@dataclass
class Account:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Account"

    @classmethod
    def to_json(cls) -> AccountJSON:
        return AccountJSON(
            kind="Account",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Account": {},
        }


SettleDTKind = typing.Union[AccountMap, Account]
SettleDTJSON = typing.Union[AccountMapJSON, AccountJSON]


def from_decoded(obj: dict) -> SettleDTKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "AccountMap" in obj:
        return AccountMap()
    if "Account" in obj:
        return Account()
    raise ValueError("Invalid enum object")


def from_json(obj: SettleDTJSON) -> SettleDTKind:
    if obj["kind"] == "AccountMap":
        return AccountMap()
    if obj["kind"] == "Account":
        return Account()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen("AccountMap" / borsh.CStruct(), "Account" / borsh.CStruct())
