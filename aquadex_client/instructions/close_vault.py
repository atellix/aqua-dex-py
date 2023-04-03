from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from ..program_id import PROGRAM_ID


class CloseVaultAccounts(typing.TypedDict):
    market: PublicKey
    admin: PublicKey
    manager: PublicKey
    owner: PublicKey
    vault: PublicKey
    fee_receiver: PublicKey


def close_vault(accounts: CloseVaultAccounts) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["admin"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["manager"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["fee_receiver"], is_signer=False, is_writable=True),
    ]
    identifier = b"\x8dg\x11~HK\x1d\x1d"
    encoded_args = b""
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
