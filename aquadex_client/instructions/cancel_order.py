from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class CancelOrderArgs(typing.TypedDict):
    inp_side: int
    inp_order_id: int


layout = borsh.CStruct("inp_side" / borsh.U8, "inp_order_id" / borsh.U128)


class CancelOrderAccounts(typing.TypedDict):
    market: PublicKey
    state: PublicKey
    agent: PublicKey
    owner: PublicKey
    user_mkt_token: PublicKey
    user_prc_token: PublicKey
    mkt_vault: PublicKey
    prc_vault: PublicKey
    orders: PublicKey
    result: PublicKey
    spl_token_prog: PublicKey


def cancel_order(
    args: CancelOrderArgs, accounts: CancelOrderAccounts
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["agent"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["user_mkt_token"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["user_prc_token"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["mkt_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["prc_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["orders"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["result"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["spl_token_prog"], is_signer=False, is_writable=False
        ),
    ]
    identifier = b"_\x81\xed\xf0\x081\xdf\x84"
    encoded_args = layout.build(
        {
            "inp_side": args["inp_side"],
            "inp_order_id": args["inp_order_id"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
