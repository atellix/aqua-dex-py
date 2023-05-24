from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class CloseAccountAccounts(typing.TypedDict):
    data_account: Pubkey
    program: Pubkey
    program_data: Pubkey
    program_admin: Pubkey


def close_account(
    accounts: CloseAccountAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["data_account"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["program_data"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program_admin"], is_signer=True, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b'}\xff\x95\x0en"H\x18'
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
