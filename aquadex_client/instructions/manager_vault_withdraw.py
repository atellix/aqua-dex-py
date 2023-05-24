from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class ManagerVaultWithdrawAccounts(typing.TypedDict):
    market: Pubkey
    state: Pubkey
    agent: Pubkey
    manager: Pubkey
    owner: Pubkey
    vault: Pubkey
    user_mkt_token: Pubkey
    user_prc_token: Pubkey
    mkt_vault: Pubkey
    prc_vault: Pubkey
    result: Pubkey
    spl_token_prog: Pubkey


def manager_vault_withdraw(
    accounts: ManagerVaultWithdrawAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["agent"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["manager"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["vault"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["user_mkt_token"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["user_prc_token"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["mkt_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["prc_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["result"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["spl_token_prog"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x1frK\xc1\xaa\x9cNv"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
