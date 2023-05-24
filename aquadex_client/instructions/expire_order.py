from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class ExpireOrderArgs(typing.TypedDict):
    inp_side: int
    inp_order_id: int
    inp_rollover: bool


layout = borsh.CStruct(
    "inp_side" / borsh.U8, "inp_order_id" / borsh.U128, "inp_rollover" / borsh.Bool
)


class ExpireOrderAccounts(typing.TypedDict):
    market: Pubkey
    state: Pubkey
    user: Pubkey
    orders: Pubkey
    settle_a: Pubkey
    settle_b: Pubkey


def expire_order(
    args: ExpireOrderArgs,
    accounts: ExpireOrderAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["user"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["orders"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_a"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_b"], is_signer=False, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xae\x1bU\xf7i\xf5\xdc\r"
    encoded_args = layout.build(
        {
            "inp_side": args["inp_side"],
            "inp_order_id": args["inp_order_id"],
            "inp_rollover": args["inp_rollover"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
