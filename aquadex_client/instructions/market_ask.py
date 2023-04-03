from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class MarketAskArgs(typing.TypedDict):
    inp_by_quantity: bool
    inp_quantity: int
    inp_net_price: int
    inp_fill: bool
    inp_preview: bool
    inp_rollover: bool


layout = borsh.CStruct(
    "inp_by_quantity" / borsh.Bool,
    "inp_quantity" / borsh.U64,
    "inp_net_price" / borsh.U64,
    "inp_fill" / borsh.Bool,
    "inp_preview" / borsh.Bool,
    "inp_rollover" / borsh.Bool,
)


class MarketAskAccounts(typing.TypedDict):
    market: PublicKey
    state: PublicKey
    agent: PublicKey
    user: PublicKey
    user_mkt_token: PublicKey
    user_prc_token: PublicKey
    mkt_vault: PublicKey
    prc_vault: PublicKey
    orders: PublicKey
    trade_log: PublicKey
    settle_a: PublicKey
    settle_b: PublicKey
    result: PublicKey
    spl_token_prog: PublicKey


def market_ask(
    args: MarketAskArgs, accounts: MarketAskAccounts
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["agent"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["user"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["user_mkt_token"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["user_prc_token"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["mkt_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["prc_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["orders"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["trade_log"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_a"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_b"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["result"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["spl_token_prog"], is_signer=False, is_writable=False
        ),
    ]
    identifier = b"\xfc\xc4L\xdc\x07\xa8OK"
    encoded_args = layout.build(
        {
            "inp_by_quantity": args["inp_by_quantity"],
            "inp_quantity": args["inp_quantity"],
            "inp_net_price": args["inp_net_price"],
            "inp_fill": args["inp_fill"],
            "inp_preview": args["inp_preview"],
            "inp_rollover": args["inp_rollover"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
