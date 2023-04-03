from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from ..program_id import PROGRAM_ID


class ManagerWithdrawAccounts(typing.TypedDict):
    market: PublicKey
    state: PublicKey
    agent: PublicKey
    manager: PublicKey
    owner: PublicKey
    user_mkt_token: PublicKey
    user_prc_token: PublicKey
    mkt_vault: PublicKey
    prc_vault: PublicKey
    settle: PublicKey
    settle_prev: PublicKey
    settle_next: PublicKey
    result: PublicKey
    spl_token_prog: PublicKey


def manager_withdraw(accounts: ManagerWithdrawAccounts) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["agent"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["manager"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["user_mkt_token"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["user_prc_token"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["mkt_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["prc_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_prev"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_next"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["result"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["spl_token_prog"], is_signer=False, is_writable=False
        ),
    ]
    identifier = b"\xc9\xf8\xbe\x8fV+\xb7\xfe"
    encoded_args = b""
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
