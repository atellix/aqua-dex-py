from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from ..program_id import PROGRAM_ID


class ExtendLogAccounts(typing.TypedDict):
    market: PublicKey
    state: PublicKey
    user: PublicKey
    settle: PublicKey


def extend_log(accounts: ExtendLogAccounts) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["user"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["settle"], is_signer=False, is_writable=True),
    ]
    identifier = b"\x7f\x9fm\xe7\x00hc\xf4"
    encoded_args = b""
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
