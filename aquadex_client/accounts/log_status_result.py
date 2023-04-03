import typing
from dataclasses import dataclass
from base64 import b64decode
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID


class LogStatusResultJSON(typing.TypedDict):
    prev: str
    next: str
    items: int


@dataclass
class LogStatusResult:
    discriminator: typing.ClassVar = b"\x15~in\xee}Q\x95"
    layout: typing.ClassVar = borsh.CStruct(
        "prev" / BorshPubkey, "next" / BorshPubkey, "items" / borsh.U32
    )
    prev: PublicKey
    next: PublicKey
    items: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: PublicKey,
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.Optional["LogStatusResult"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp["result"]["value"]
        if info is None:
            return None
        if info["owner"] != str(PROGRAM_ID):
            raise ValueError("Account does not belong to this program")
        bytes_data = b64decode(info["data"][0])
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[PublicKey],
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.List[typing.Optional["LogStatusResult"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["LogStatusResult"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != PROGRAM_ID:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "LogStatusResult":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = LogStatusResult.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            prev=dec.prev,
            next=dec.next,
            items=dec.items,
        )

    def to_json(self) -> LogStatusResultJSON:
        return {
            "prev": str(self.prev),
            "next": str(self.next),
            "items": self.items,
        }

    @classmethod
    def from_json(cls, obj: LogStatusResultJSON) -> "LogStatusResult":
        return cls(
            prev=PublicKey(obj["prev"]),
            next=PublicKey(obj["next"]),
            items=obj["items"],
        )
