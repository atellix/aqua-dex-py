from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class SPLTokenJSON(typing.TypedDict):
    kind: typing.Literal["SPLToken"]


class AtxSecurityTokenJSON(typing.TypedDict):
    kind: typing.Literal["AtxSecurityToken"]


@dataclass
class SPLToken:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "SPLToken"

    @classmethod
    def to_json(cls) -> SPLTokenJSON:
        return SPLTokenJSON(
            kind="SPLToken",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "SPLToken": {},
        }


@dataclass
class AtxSecurityToken:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "AtxSecurityToken"

    @classmethod
    def to_json(cls) -> AtxSecurityTokenJSON:
        return AtxSecurityTokenJSON(
            kind="AtxSecurityToken",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AtxSecurityToken": {},
        }


MintTypeKind = typing.Union[SPLToken, AtxSecurityToken]
MintTypeJSON = typing.Union[SPLTokenJSON, AtxSecurityTokenJSON]


def from_decoded(obj: dict) -> MintTypeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "SPLToken" in obj:
        return SPLToken()
    if "AtxSecurityToken" in obj:
        return AtxSecurityToken()
    raise ValueError("Invalid enum object")


def from_json(obj: MintTypeJSON) -> MintTypeKind:
    if obj["kind"] == "SPLToken":
        return SPLToken()
    if obj["kind"] == "AtxSecurityToken":
        return AtxSecurityToken()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "SPLToken" / borsh.CStruct(), "AtxSecurityToken" / borsh.CStruct()
)
