from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class ManagerCancelOrderArgs(typing.TypedDict):
    inp_side: int
    inp_order_id: int
    inp_rollover: bool


layout = borsh.CStruct(
    "inp_side" / borsh.U8, "inp_order_id" / borsh.U128, "inp_rollover" / borsh.Bool
)


class ManagerCancelOrderAccounts(typing.TypedDict):
    market: PublicKey
    state: PublicKey
    manager: PublicKey
    orders: PublicKey
    result: PublicKey
    settle_a: PublicKey
    settle_b: PublicKey


def manager_cancel_order(
    args: ManagerCancelOrderArgs, accounts: ManagerCancelOrderAccounts
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["manager"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["orders"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["result"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["settle_a"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_b"], is_signer=False, is_writable=True),
    ]
    identifier = b"\x1duuJ\x9f\xc2\xf0\xa7"
    encoded_args = layout.build(
        {
            "inp_side": args["inp_side"],
            "inp_order_id": args["inp_order_id"],
            "inp_rollover": args["inp_rollover"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
