from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from ..program_id import PROGRAM_ID


class LogStatusAccounts(typing.TypedDict):
    settle: PublicKey


def log_status(accounts: LogStatusAccounts) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["settle"], is_signer=False, is_writable=False)
    ]
    identifier = b"\\\xce\xb08l\x90\x17k"
    encoded_args = b""
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
