from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class BidOrderMapJSON(typing.TypedDict):
    kind: typing.Literal["BidOrderMap"]


class BidOrderJSON(typing.TypedDict):
    kind: typing.Literal["BidOrder"]


class AskOrderMapJSON(typing.TypedDict):
    kind: typing.Literal["AskOrderMap"]


class AskOrderJSON(typing.TypedDict):
    kind: typing.Literal["AskOrder"]


class AccountMapJSON(typing.TypedDict):
    kind: typing.Literal["AccountMap"]


class AccountJSON(typing.TypedDict):
    kind: typing.Literal["Account"]


class UserRBACMapJSON(typing.TypedDict):
    kind: typing.Literal["UserRBACMap"]


class UserRBACJSON(typing.TypedDict):
    kind: typing.Literal["UserRBAC"]


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
class BidOrder:
    discriminator: typing.ClassVar = 1
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
class AskOrderMap:
    discriminator: typing.ClassVar = 2
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


@dataclass
class AccountMap:
    discriminator: typing.ClassVar = 4
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
    discriminator: typing.ClassVar = 5
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


@dataclass
class UserRBACMap:
    discriminator: typing.ClassVar = 6
    kind: typing.ClassVar = "UserRBACMap"

    @classmethod
    def to_json(cls) -> UserRBACMapJSON:
        return UserRBACMapJSON(
            kind="UserRBACMap",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UserRBACMap": {},
        }


@dataclass
class UserRBAC:
    discriminator: typing.ClassVar = 7
    kind: typing.ClassVar = "UserRBAC"

    @classmethod
    def to_json(cls) -> UserRBACJSON:
        return UserRBACJSON(
            kind="UserRBAC",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UserRBAC": {},
        }


DTKind = typing.Union[
    BidOrderMap,
    BidOrder,
    AskOrderMap,
    AskOrder,
    AccountMap,
    Account,
    UserRBACMap,
    UserRBAC,
]
DTJSON = typing.Union[
    BidOrderMapJSON,
    BidOrderJSON,
    AskOrderMapJSON,
    AskOrderJSON,
    AccountMapJSON,
    AccountJSON,
    UserRBACMapJSON,
    UserRBACJSON,
]


def from_decoded(obj: dict) -> DTKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "BidOrderMap" in obj:
        return BidOrderMap()
    if "BidOrder" in obj:
        return BidOrder()
    if "AskOrderMap" in obj:
        return AskOrderMap()
    if "AskOrder" in obj:
        return AskOrder()
    if "AccountMap" in obj:
        return AccountMap()
    if "Account" in obj:
        return Account()
    if "UserRBACMap" in obj:
        return UserRBACMap()
    if "UserRBAC" in obj:
        return UserRBAC()
    raise ValueError("Invalid enum object")


def from_json(obj: DTJSON) -> DTKind:
    if obj["kind"] == "BidOrderMap":
        return BidOrderMap()
    if obj["kind"] == "BidOrder":
        return BidOrder()
    if obj["kind"] == "AskOrderMap":
        return AskOrderMap()
    if obj["kind"] == "AskOrder":
        return AskOrder()
    if obj["kind"] == "AccountMap":
        return AccountMap()
    if obj["kind"] == "Account":
        return Account()
    if obj["kind"] == "UserRBACMap":
        return UserRBACMap()
    if obj["kind"] == "UserRBAC":
        return UserRBAC()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "BidOrderMap" / borsh.CStruct(),
    "BidOrder" / borsh.CStruct(),
    "AskOrderMap" / borsh.CStruct(),
    "AskOrder" / borsh.CStruct(),
    "AccountMap" / borsh.CStruct(),
    "Account" / borsh.CStruct(),
    "UserRBACMap" / borsh.CStruct(),
    "UserRBAC" / borsh.CStruct(),
)
