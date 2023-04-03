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
from ..program_id import PROGRAM_ID


class WithdrawResultJSON(typing.TypedDict):
    mkt_tokens: int
    prc_tokens: int


@dataclass
class WithdrawResult:
    discriminator: typing.ClassVar = b"hv_NkN\t%"
    layout: typing.ClassVar = borsh.CStruct(
        "mkt_tokens" / borsh.U64, "prc_tokens" / borsh.U64
    )
    mkt_tokens: int
    prc_tokens: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: PublicKey,
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.Optional["WithdrawResult"]:
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
    ) -> typing.List[typing.Optional["WithdrawResult"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["WithdrawResult"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != PROGRAM_ID:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "WithdrawResult":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = WithdrawResult.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            mkt_tokens=dec.mkt_tokens,
            prc_tokens=dec.prc_tokens,
        )

    def to_json(self) -> WithdrawResultJSON:
        return {
            "mkt_tokens": self.mkt_tokens,
            "prc_tokens": self.prc_tokens,
        }

    @classmethod
    def from_json(cls, obj: WithdrawResultJSON) -> "WithdrawResult":
        return cls(
            mkt_tokens=obj["mkt_tokens"],
            prc_tokens=obj["prc_tokens"],
        )
