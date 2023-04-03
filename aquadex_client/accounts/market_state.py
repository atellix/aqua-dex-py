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


class MarketStateJSON(typing.TypedDict):
    settle_a: str
    settle_b: str
    log_rollover: bool
    log_deposit_balance: int
    action_counter: int
    order_counter: int
    active_bid: int
    active_ask: int
    mkt_vault_balance: int
    mkt_order_balance: int
    mkt_user_vault_balance: int
    mkt_log_balance: int
    prc_vault_balance: int
    prc_order_balance: int
    prc_user_vault_balance: int
    prc_log_balance: int
    prc_fees_balance: int
    last_ts: int
    last_price: int


@dataclass
class MarketState:
    discriminator: typing.ClassVar = b"\x00}{\xd7_`\xa4\xc2"
    layout: typing.ClassVar = borsh.CStruct(
        "settle_a" / BorshPubkey,
        "settle_b" / BorshPubkey,
        "log_rollover" / borsh.Bool,
        "log_deposit_balance" / borsh.U64,
        "action_counter" / borsh.U64,
        "order_counter" / borsh.U64,
        "active_bid" / borsh.U32,
        "active_ask" / borsh.U32,
        "mkt_vault_balance" / borsh.U64,
        "mkt_order_balance" / borsh.U64,
        "mkt_user_vault_balance" / borsh.U64,
        "mkt_log_balance" / borsh.U64,
        "prc_vault_balance" / borsh.U64,
        "prc_order_balance" / borsh.U64,
        "prc_user_vault_balance" / borsh.U64,
        "prc_log_balance" / borsh.U64,
        "prc_fees_balance" / borsh.U64,
        "last_ts" / borsh.I64,
        "last_price" / borsh.U64,
    )
    settle_a: PublicKey
    settle_b: PublicKey
    log_rollover: bool
    log_deposit_balance: int
    action_counter: int
    order_counter: int
    active_bid: int
    active_ask: int
    mkt_vault_balance: int
    mkt_order_balance: int
    mkt_user_vault_balance: int
    mkt_log_balance: int
    prc_vault_balance: int
    prc_order_balance: int
    prc_user_vault_balance: int
    prc_log_balance: int
    prc_fees_balance: int
    last_ts: int
    last_price: int

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: PublicKey,
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.Optional["MarketState"]:
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
    ) -> typing.List[typing.Optional["MarketState"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["MarketState"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != PROGRAM_ID:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "MarketState":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = MarketState.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            settle_a=dec.settle_a,
            settle_b=dec.settle_b,
            log_rollover=dec.log_rollover,
            log_deposit_balance=dec.log_deposit_balance,
            action_counter=dec.action_counter,
            order_counter=dec.order_counter,
            active_bid=dec.active_bid,
            active_ask=dec.active_ask,
            mkt_vault_balance=dec.mkt_vault_balance,
            mkt_order_balance=dec.mkt_order_balance,
            mkt_user_vault_balance=dec.mkt_user_vault_balance,
            mkt_log_balance=dec.mkt_log_balance,
            prc_vault_balance=dec.prc_vault_balance,
            prc_order_balance=dec.prc_order_balance,
            prc_user_vault_balance=dec.prc_user_vault_balance,
            prc_log_balance=dec.prc_log_balance,
            prc_fees_balance=dec.prc_fees_balance,
            last_ts=dec.last_ts,
            last_price=dec.last_price,
        )

    def to_json(self) -> MarketStateJSON:
        return {
            "settle_a": str(self.settle_a),
            "settle_b": str(self.settle_b),
            "log_rollover": self.log_rollover,
            "log_deposit_balance": self.log_deposit_balance,
            "action_counter": self.action_counter,
            "order_counter": self.order_counter,
            "active_bid": self.active_bid,
            "active_ask": self.active_ask,
            "mkt_vault_balance": self.mkt_vault_balance,
            "mkt_order_balance": self.mkt_order_balance,
            "mkt_user_vault_balance": self.mkt_user_vault_balance,
            "mkt_log_balance": self.mkt_log_balance,
            "prc_vault_balance": self.prc_vault_balance,
            "prc_order_balance": self.prc_order_balance,
            "prc_user_vault_balance": self.prc_user_vault_balance,
            "prc_log_balance": self.prc_log_balance,
            "prc_fees_balance": self.prc_fees_balance,
            "last_ts": self.last_ts,
            "last_price": self.last_price,
        }

    @classmethod
    def from_json(cls, obj: MarketStateJSON) -> "MarketState":
        return cls(
            settle_a=PublicKey(obj["settle_a"]),
            settle_b=PublicKey(obj["settle_b"]),
            log_rollover=obj["log_rollover"],
            log_deposit_balance=obj["log_deposit_balance"],
            action_counter=obj["action_counter"],
            order_counter=obj["order_counter"],
            active_bid=obj["active_bid"],
            active_ask=obj["active_ask"],
            mkt_vault_balance=obj["mkt_vault_balance"],
            mkt_order_balance=obj["mkt_order_balance"],
            mkt_user_vault_balance=obj["mkt_user_vault_balance"],
            mkt_log_balance=obj["mkt_log_balance"],
            prc_vault_balance=obj["prc_vault_balance"],
            prc_order_balance=obj["prc_order_balance"],
            prc_user_vault_balance=obj["prc_user_vault_balance"],
            prc_log_balance=obj["prc_log_balance"],
            prc_fees_balance=obj["prc_fees_balance"],
            last_ts=obj["last_ts"],
            last_price=obj["last_price"],
        )
