from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class LogStatusAccounts(typing.TypedDict):
    settle: Pubkey


def log_status(
    accounts: LogStatusAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["settle"], is_signer=False, is_writable=False)
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\\\xce\xb08l\x90\x17k"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
