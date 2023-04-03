from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from ..program_id import PROGRAM_ID


class InitializeAccounts(typing.TypedDict):
    root_data: PublicKey
    auth_data: PublicKey
    program: PublicKey
    program_data: PublicKey
    program_admin: PublicKey
    system_program: PublicKey


def initialize(accounts: InitializeAccounts) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["root_data"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["auth_data"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["program"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["program_data"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["program_admin"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["system_program"], is_signer=False, is_writable=False
        ),
    ]
    identifier = b"\xaf\xafm\x1f\r\x98\x9b\xed"
    encoded_args = b""
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
