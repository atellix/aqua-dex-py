from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class ManagerUpdateMarketArgs(typing.TypedDict):
    inp_active: bool
    inp_expire_enable: bool
    inp_expire_min: int
    inp_min_quantity: int
    inp_tick_decimals: int
    inp_taker_fee: int
    inp_maker_rebate: int
    inp_log_fee: int
    inp_log_rebate: int
    inp_log_reimburse: int


layout = borsh.CStruct(
    "inp_active" / borsh.Bool,
    "inp_expire_enable" / borsh.Bool,
    "inp_expire_min" / borsh.I64,
    "inp_min_quantity" / borsh.U64,
    "inp_tick_decimals" / borsh.U8,
    "inp_taker_fee" / borsh.U32,
    "inp_maker_rebate" / borsh.U32,
    "inp_log_fee" / borsh.U64,
    "inp_log_rebate" / borsh.U64,
    "inp_log_reimburse" / borsh.U64,
)


class ManagerUpdateMarketAccounts(typing.TypedDict):
    market: PublicKey
    admin: PublicKey
    manager: PublicKey
    fee_manager: PublicKey
    vault_manager: PublicKey


def manager_update_market(
    args: ManagerUpdateMarketArgs, accounts: ManagerUpdateMarketAccounts
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["admin"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["manager"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["fee_manager"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["vault_manager"], is_signer=False, is_writable=False
        ),
    ]
    identifier = b"3\x13\x91\x98\x90\x90bM"
    encoded_args = layout.build(
        {
            "inp_active": args["inp_active"],
            "inp_expire_enable": args["inp_expire_enable"],
            "inp_expire_min": args["inp_expire_min"],
            "inp_min_quantity": args["inp_min_quantity"],
            "inp_tick_decimals": args["inp_tick_decimals"],
            "inp_taker_fee": args["inp_taker_fee"],
            "inp_maker_rebate": args["inp_maker_rebate"],
            "inp_log_fee": args["inp_log_fee"],
            "inp_log_rebate": args["inp_log_rebate"],
            "inp_log_reimburse": args["inp_log_reimburse"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
