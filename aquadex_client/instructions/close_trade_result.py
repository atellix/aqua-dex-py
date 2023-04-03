from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from ..program_id import PROGRAM_ID


class CloseTradeResultAccounts(typing.TypedDict):
    fee_receiver: PublicKey
    result: PublicKey


def close_trade_result(accounts: CloseTradeResultAccounts) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["fee_receiver"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["result"], is_signer=True, is_writable=True),
    ]
    identifier = b"\xd13\n<\x94\x8d1\xfd"
    encoded_args = b""
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
