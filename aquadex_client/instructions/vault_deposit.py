from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class VaultDepositAccounts(typing.TypedDict):
    market: Pubkey
    state: Pubkey
    admin: Pubkey
    manager: Pubkey
    owner: Pubkey
    settle: Pubkey
    settle_prev: Pubkey
    settle_next: Pubkey
    vault: Pubkey


def vault_deposit(
    accounts: VaultDepositAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["admin"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["manager"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["settle"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_prev"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_next"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xe7\x96)q\xb4h\xa2x"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
