from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class NetworkAdminJSON(typing.TypedDict):
    kind: typing.Literal["NetworkAdmin"]


class FeeManagerJSON(typing.TypedDict):
    kind: typing.Literal["FeeManager"]


@dataclass
class NetworkAdmin:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "NetworkAdmin"

    @classmethod
    def to_json(cls) -> NetworkAdminJSON:
        return NetworkAdminJSON(
            kind="NetworkAdmin",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "NetworkAdmin": {},
        }


@dataclass
class FeeManager:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "FeeManager"

    @classmethod
    def to_json(cls) -> FeeManagerJSON:
        return FeeManagerJSON(
            kind="FeeManager",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "FeeManager": {},
        }


RoleKind = typing.Union[NetworkAdmin, FeeManager]
RoleJSON = typing.Union[NetworkAdminJSON, FeeManagerJSON]


def from_decoded(obj: dict) -> RoleKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "NetworkAdmin" in obj:
        return NetworkAdmin()
    if "FeeManager" in obj:
        return FeeManager()
    raise ValueError("Invalid enum object")


def from_json(obj: RoleJSON) -> RoleKind:
    if obj["kind"] == "NetworkAdmin":
        return NetworkAdmin()
    if obj["kind"] == "FeeManager":
        return FeeManager()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "NetworkAdmin" / borsh.CStruct(), "FeeManager" / borsh.CStruct()
)
