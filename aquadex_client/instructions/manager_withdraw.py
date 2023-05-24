from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class ManagerWithdrawAccounts(typing.TypedDict):
    market: Pubkey
    state: Pubkey
    agent: Pubkey
    manager: Pubkey
    owner: Pubkey
    user_mkt_token: Pubkey
    user_prc_token: Pubkey
    mkt_vault: Pubkey
    prc_vault: Pubkey
    settle: Pubkey
    settle_prev: Pubkey
    settle_next: Pubkey
    result: Pubkey
    spl_token_prog: Pubkey


def manager_withdraw(
    accounts: ManagerWithdrawAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["agent"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["manager"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["user_mkt_token"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["user_prc_token"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["mkt_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["prc_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_prev"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_next"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["result"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["spl_token_prog"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xc9\xf8\xbe\x8fV+\xb7\xfe"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
