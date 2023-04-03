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


class UserVaultJSON(typing.TypedDict):
    initialized: bool
    market: str
    owner: str
    mkt_tokens: int
    prc_tokens: int


@dataclass
class UserVault:
    discriminator: typing.ClassVar = b"\x17L`\x9f\xd2\n\x05\x16"
    layout: typing.ClassVar = borsh.CStruct(
        "initialized" / borsh.Bool,
        "market" / BorshPubkey,
        "owner" / BorshPubkey,
        "mkt_tokens" / borsh.U64,
        "prc_tokens" / borsh.U64,
    )
    initialized: bool
    market: PublicKey
    owner: PublicKey
    mkt_tokens: int
    prc_tokens: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: PublicKey,
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.Optional["UserVault"]:
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
    ) -> typing.List[typing.Optional["UserVault"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["UserVault"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != PROGRAM_ID:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "UserVault":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = UserVault.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            initialized=dec.initialized,
            market=dec.market,
            owner=dec.owner,
            mkt_tokens=dec.mkt_tokens,
            prc_tokens=dec.prc_tokens,
        )

    def to_json(self) -> UserVaultJSON:
        return {
            "initialized": self.initialized,
            "market": str(self.market),
            "owner": str(self.owner),
            "mkt_tokens": self.mkt_tokens,
            "prc_tokens": self.prc_tokens,
        }

    @classmethod
    def from_json(cls, obj: UserVaultJSON) -> "UserVault":
        return cls(
            initialized=obj["initialized"],
            market=PublicKey(obj["market"]),
            owner=PublicKey(obj["owner"]),
            mkt_tokens=obj["mkt_tokens"],
            prc_tokens=obj["prc_tokens"],
        )
