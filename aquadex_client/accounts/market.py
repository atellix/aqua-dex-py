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


class MarketJSON(typing.TypedDict):
    active: bool
    manager_actions: bool
    expire_enable: bool
    expire_min: int
    min_quantity: int
    tick_decimals: int
    log_fee: int
    log_rebate: int
    log_reimburse: int
    taker_fee: int
    maker_rebate: int
    state: str
    trade_log: str
    agent: str
    agent_nonce: int
    manager: str
    mkt_mint: str
    mkt_vault: str
    mkt_decimals: int
    mkt_mint_type: int
    prc_mint: str
    prc_vault: str
    prc_decimals: int
    prc_mint_type: int
    orders: str
    settle0: str


@dataclass
class Market:
    discriminator: typing.ClassVar = b"\xdb\xbe\xd57\x00\xe3\xc6\x9a"
    layout: typing.ClassVar = borsh.CStruct(
        "active" / borsh.Bool,
        "manager_actions" / borsh.Bool,
        "expire_enable" / borsh.Bool,
        "expire_min" / borsh.I64,
        "min_quantity" / borsh.U64,
        "tick_decimals" / borsh.U8,
        "log_fee" / borsh.U64,
        "log_rebate" / borsh.U64,
        "log_reimburse" / borsh.U64,
        "taker_fee" / borsh.U32,
        "maker_rebate" / borsh.U32,
        "state" / BorshPubkey,
        "trade_log" / BorshPubkey,
        "agent" / BorshPubkey,
        "agent_nonce" / borsh.U8,
        "manager" / BorshPubkey,
        "mkt_mint" / BorshPubkey,
        "mkt_vault" / BorshPubkey,
        "mkt_decimals" / borsh.U8,
        "mkt_mint_type" / borsh.U8,
        "prc_mint" / BorshPubkey,
        "prc_vault" / BorshPubkey,
        "prc_decimals" / borsh.U8,
        "prc_mint_type" / borsh.U8,
        "orders" / BorshPubkey,
        "settle0" / BorshPubkey,
    )
    active: bool
    manager_actions: bool
    expire_enable: bool
    expire_min: int
    min_quantity: int
    tick_decimals: int
    log_fee: int
    log_rebate: int
    log_reimburse: int
    taker_fee: int
    maker_rebate: int
    state: PublicKey
    trade_log: PublicKey
    agent: PublicKey
    agent_nonce: int
    manager: PublicKey
    mkt_mint: PublicKey
    mkt_vault: PublicKey
    mkt_decimals: int
    mkt_mint_type: int
    prc_mint: PublicKey
    prc_vault: PublicKey
    prc_decimals: int
    prc_mint_type: int
    orders: PublicKey
    settle0: PublicKey

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: PublicKey,
        commitment: typing.Optional[Commitment] = None,
    ) -> typing.Optional["Market"]:
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
    ) -> typing.List[typing.Optional["Market"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Market"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != PROGRAM_ID:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Market":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Market.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            active=dec.active,
            manager_actions=dec.manager_actions,
            expire_enable=dec.expire_enable,
            expire_min=dec.expire_min,
            min_quantity=dec.min_quantity,
            tick_decimals=dec.tick_decimals,
            log_fee=dec.log_fee,
            log_rebate=dec.log_rebate,
            log_reimburse=dec.log_reimburse,
            taker_fee=dec.taker_fee,
            maker_rebate=dec.maker_rebate,
            state=dec.state,
            trade_log=dec.trade_log,
            agent=dec.agent,
            agent_nonce=dec.agent_nonce,
            manager=dec.manager,
            mkt_mint=dec.mkt_mint,
            mkt_vault=dec.mkt_vault,
            mkt_decimals=dec.mkt_decimals,
            mkt_mint_type=dec.mkt_mint_type,
            prc_mint=dec.prc_mint,
            prc_vault=dec.prc_vault,
            prc_decimals=dec.prc_decimals,
            prc_mint_type=dec.prc_mint_type,
            orders=dec.orders,
            settle0=dec.settle0,
        )

    def to_json(self) -> MarketJSON:
        return {
            "active": self.active,
            "manager_actions": self.manager_actions,
            "expire_enable": self.expire_enable,
            "expire_min": self.expire_min,
            "min_quantity": self.min_quantity,
            "tick_decimals": self.tick_decimals,
            "log_fee": self.log_fee,
            "log_rebate": self.log_rebate,
            "log_reimburse": self.log_reimburse,
            "taker_fee": self.taker_fee,
            "maker_rebate": self.maker_rebate,
            "state": str(self.state),
            "trade_log": str(self.trade_log),
            "agent": str(self.agent),
            "agent_nonce": self.agent_nonce,
            "manager": str(self.manager),
            "mkt_mint": str(self.mkt_mint),
            "mkt_vault": str(self.mkt_vault),
            "mkt_decimals": self.mkt_decimals,
            "mkt_mint_type": self.mkt_mint_type,
            "prc_mint": str(self.prc_mint),
            "prc_vault": str(self.prc_vault),
            "prc_decimals": self.prc_decimals,
            "prc_mint_type": self.prc_mint_type,
            "orders": str(self.orders),
            "settle0": str(self.settle0),
        }

    @classmethod
    def from_json(cls, obj: MarketJSON) -> "Market":
        return cls(
            active=obj["active"],
            manager_actions=obj["manager_actions"],
            expire_enable=obj["expire_enable"],
            expire_min=obj["expire_min"],
            min_quantity=obj["min_quantity"],
            tick_decimals=obj["tick_decimals"],
            log_fee=obj["log_fee"],
            log_rebate=obj["log_rebate"],
            log_reimburse=obj["log_reimburse"],
            taker_fee=obj["taker_fee"],
            maker_rebate=obj["maker_rebate"],
            state=PublicKey(obj["state"]),
            trade_log=PublicKey(obj["trade_log"]),
            agent=PublicKey(obj["agent"]),
            agent_nonce=obj["agent_nonce"],
            manager=PublicKey(obj["manager"]),
            mkt_mint=PublicKey(obj["mkt_mint"]),
            mkt_vault=PublicKey(obj["mkt_vault"]),
            mkt_decimals=obj["mkt_decimals"],
            mkt_mint_type=obj["mkt_mint_type"],
            prc_mint=PublicKey(obj["prc_mint"]),
            prc_vault=PublicKey(obj["prc_vault"]),
            prc_decimals=obj["prc_decimals"],
            prc_mint_type=obj["prc_mint_type"],
            orders=PublicKey(obj["orders"]),
            settle0=PublicKey(obj["settle0"]),
        )
