from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class ExtendLogAccounts(typing.TypedDict):
    market: Pubkey
    state: Pubkey
    user: Pubkey
    settle: Pubkey


def extend_log(
    accounts: ExtendLogAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["user"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["settle"], is_signer=False, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x7f\x9fm\xe7\x00hc\xf4"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
