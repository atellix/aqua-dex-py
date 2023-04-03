from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from ..program_id import PROGRAM_ID


class ManagerWithdrawFeesAccounts(typing.TypedDict):
    root_data: PublicKey
    auth_data: PublicKey
    market: PublicKey
    state: PublicKey
    agent: PublicKey
    admin: PublicKey
    manager: PublicKey
    manager_prc_token: PublicKey
    prc_vault: PublicKey
    spl_token_prog: PublicKey


def manager_withdraw_fees(
    accounts: ManagerWithdrawFeesAccounts,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["root_data"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["auth_data"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["agent"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["admin"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["manager"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["manager_prc_token"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["prc_vault"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["spl_token_prog"], is_signer=False, is_writable=False
        ),
    ]
    identifier = b"\xf3\x92\x807\xdc.z)"
    encoded_args = b""
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
