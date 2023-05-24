from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class CancelOrderArgs(typing.TypedDict):
    inp_side: int
    inp_order_id: int


layout = borsh.CStruct("inp_side" / borsh.U8, "inp_order_id" / borsh.U128)


class CancelOrderAccounts(typing.TypedDict):
    market: Pubkey
    state: Pubkey
    agent: Pubkey
    owner: Pubkey
    user_mkt_token: Pubkey
    user_prc_token: Pubkey
    mkt_vault: Pubkey
    prc_vault: Pubkey
    orders: Pubkey
    result: Pubkey
    spl_token_prog: Pubkey


def cancel_order(
    args: CancelOrderArgs,
    accounts: CancelOrderAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
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
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"_\x81\xed\xf0\x081\xdf\x84"
    encoded_args = layout.build(
        {
            "inp_side": args["inp_side"],
            "inp_order_id": args["inp_order_id"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
