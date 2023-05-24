from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class ManagerWithdrawFeesAccounts(typing.TypedDict):
    root_data: Pubkey
    auth_data: Pubkey
    market: Pubkey
    state: Pubkey
    agent: Pubkey
    admin: Pubkey
    manager: Pubkey
    manager_prc_token: Pubkey
    prc_vault: Pubkey
    spl_token_prog: Pubkey


def manager_withdraw_fees(
    accounts: ManagerWithdrawFeesAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["root_data"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["auth_data"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["agent"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["admin"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["manager"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["manager_prc_token"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["prc_vault"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["spl_token_prog"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xf3\x92\x807\xdc.z)"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
