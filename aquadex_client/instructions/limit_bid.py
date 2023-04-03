from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class LimitBidArgs(typing.TypedDict):
    inp_quantity: int
    inp_price_request: int
    inp_post: bool
    inp_fill: bool
    inp_expires: int
    inp_preview: bool
    inp_rollover: bool


layout = borsh.CStruct(
    "inp_quantity" / borsh.U64,
    "inp_price_request" / borsh.U64,
    "inp_post" / borsh.Bool,
    "inp_fill" / borsh.Bool,
    "inp_expires" / borsh.I64,
    "inp_preview" / borsh.Bool,
    "inp_rollover" / borsh.Bool,
)


class LimitBidAccounts(typing.TypedDict):
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


def limit_bid(args: LimitBidArgs, accounts: LimitBidAccounts) -> TransactionInstruction:
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
    identifier = b"\xbcNg$\xc4\x93\x9c\x1f"
    encoded_args = layout.build(
        {
            "inp_quantity": args["inp_quantity"],
            "inp_price_request": args["inp_price_request"],
            "inp_post": args["inp_post"],
            "inp_fill": args["inp_fill"],
            "inp_expires": args["inp_expires"],
            "inp_preview": args["inp_preview"],
            "inp_rollover": args["inp_rollover"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
