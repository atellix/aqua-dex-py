from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from ..program_id import PROGRAM_ID


class VaultDepositAccounts(typing.TypedDict):
    market: PublicKey
    state: PublicKey
    admin: PublicKey
    manager: PublicKey
    owner: PublicKey
    settle: PublicKey
    settle_prev: PublicKey
    settle_next: PublicKey
    vault: PublicKey
    system_program: PublicKey


def vault_deposit(accounts: VaultDepositAccounts) -> TransactionInstruction:
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
        AccountMeta(
            pubkey=accounts["system_program"], is_signer=False, is_writable=False
        ),
    ]
    identifier = b"\xe7\x96)q\xb4h\xa2x"
    encoded_args = b""
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
