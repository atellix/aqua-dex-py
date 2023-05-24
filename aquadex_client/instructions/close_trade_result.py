from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class CloseTradeResultAccounts(typing.TypedDict):
    fee_receiver: Pubkey
    result: Pubkey


def close_trade_result(
    accounts: CloseTradeResultAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["fee_receiver"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["result"], is_signer=True, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xd13\n<\x94\x8d1\xfd"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
