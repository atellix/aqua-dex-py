from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from ..program_id import PROGRAM_ID


class CloseWithdrawResultAccounts(typing.TypedDict):
    fee_receiver: PublicKey
    result: PublicKey


def close_withdraw_result(
    accounts: CloseWithdrawResultAccounts,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["fee_receiver"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["result"], is_signer=True, is_writable=True),
    ]
    identifier = b"\x94\x11aM^e\xbap"
    encoded_args = b""
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
