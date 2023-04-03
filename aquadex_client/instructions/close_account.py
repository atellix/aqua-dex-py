from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from ..program_id import PROGRAM_ID


class CloseAccountAccounts(typing.TypedDict):
    data_account: PublicKey
    program: PublicKey
    program_data: PublicKey
    program_admin: PublicKey


def close_account(accounts: CloseAccountAccounts) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["data_account"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["program_data"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program_admin"], is_signer=True, is_writable=True),
    ]
    identifier = b'}\xff\x95\x0en"H\x18'
    encoded_args = b""
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
