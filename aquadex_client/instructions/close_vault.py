from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class CloseVaultAccounts(typing.TypedDict):
    market: Pubkey
    admin: Pubkey
    manager: Pubkey
    owner: Pubkey
    vault: Pubkey
    fee_receiver: Pubkey


def close_vault(
    accounts: CloseVaultAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["admin"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["manager"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["fee_receiver"], is_signer=False, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x8dg\x11~HK\x1d\x1d"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
