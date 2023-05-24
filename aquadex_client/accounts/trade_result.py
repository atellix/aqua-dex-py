import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from ..program_id import PROGRAM_ID


class TradeResultJSON(typing.TypedDict):
    tokens_received: int
    tokens_sent: int
    tokens_fee: int
    posted_quantity: int
    order_id: int


@dataclass
class TradeResult:
    discriminator: typing.ClassVar = b"8x3\xcd\x9fI\xffs"
    layout: typing.ClassVar = borsh.CStruct(
        "tokens_received" / borsh.U64,
        "tokens_sent" / borsh.U64,
        "tokens_fee" / borsh.U64,
        "posted_quantity" / borsh.U64,
        "order_id" / borsh.U128,
    )
    tokens_received: int
    tokens_sent: int
    tokens_fee: int
    posted_quantity: int
    order_id: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["TradeResult"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id:
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[Pubkey],
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["TradeResult"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["TradeResult"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "TradeResult":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = TradeResult.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            tokens_received=dec.tokens_received,
            tokens_sent=dec.tokens_sent,
            tokens_fee=dec.tokens_fee,
            posted_quantity=dec.posted_quantity,
            order_id=dec.order_id,
        )

    def to_json(self) -> TradeResultJSON:
        return {
            "tokens_received": self.tokens_received,
            "tokens_sent": self.tokens_sent,
            "tokens_fee": self.tokens_fee,
            "posted_quantity": self.posted_quantity,
            "order_id": self.order_id,
        }

    @classmethod
    def from_json(cls, obj: TradeResultJSON) -> "TradeResult":
        return cls(
            tokens_received=obj["tokens_received"],
            tokens_sent=obj["tokens_sent"],
            tokens_fee=obj["tokens_fee"],
            posted_quantity=obj["posted_quantity"],
            order_id=obj["order_id"],
        )
