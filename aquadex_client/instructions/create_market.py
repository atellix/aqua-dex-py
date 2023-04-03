from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class CreateMarketArgs(typing.TypedDict):
    inp_agent_nonce: int
    inp_mkt_vault_nonce: int
    inp_prc_vault_nonce: int
    inp_mkt_decimals: int
    inp_prc_decimals: int
    inp_mkt_mint_type: int
    inp_prc_mint_type: int
    inp_manager_actions: bool
    inp_expire_enable: bool
    inp_expire_min: int
    inp_min_quantity: int
    inp_tick_decimals: int
    inp_taker_fee: int
    inp_maker_rebate: int
    inp_log_fee: int
    inp_log_rebate: int
    inp_log_reimburse: int
    inp_mkt_vault_uuid: int
    inp_prc_vault_uuid: int


layout = borsh.CStruct(
    "inp_agent_nonce" / borsh.U8,
    "inp_mkt_vault_nonce" / borsh.U8,
    "inp_prc_vault_nonce" / borsh.U8,
    "inp_mkt_decimals" / borsh.U8,
    "inp_prc_decimals" / borsh.U8,
    "inp_mkt_mint_type" / borsh.U8,
    "inp_prc_mint_type" / borsh.U8,
    "inp_manager_actions" / borsh.Bool,
    "inp_expire_enable" / borsh.Bool,
    "inp_expire_min" / borsh.I64,
    "inp_min_quantity" / borsh.U64,
    "inp_tick_decimals" / borsh.U8,
    "inp_taker_fee" / borsh.U32,
    "inp_maker_rebate" / borsh.U32,
    "inp_log_fee" / borsh.U64,
    "inp_log_rebate" / borsh.U64,
    "inp_log_reimburse" / borsh.U64,
    "inp_mkt_vault_uuid" / borsh.U128,
    "inp_prc_vault_uuid" / borsh.U128,
)


class CreateMarketAccounts(typing.TypedDict):
    market: PublicKey
    state: PublicKey
    admin: PublicKey
    agent: PublicKey
    manager: PublicKey
    fee_manager: PublicKey
    vault_manager: PublicKey
    mkt_mint: PublicKey
    mkt_vault: PublicKey
    prc_mint: PublicKey
    prc_vault: PublicKey
    trade_log: PublicKey
    orders: PublicKey
    settle_a: PublicKey
    settle_b: PublicKey
    spl_token_prog: PublicKey
    asc_token_prog: PublicKey
    system_program: PublicKey
    system_rent: PublicKey


def create_market(
    args: CreateMarketArgs, accounts: CreateMarketAccounts
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["admin"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["agent"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["manager"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["fee_manager"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["vault_manager"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["mkt_mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["mkt_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["prc_mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["prc_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["trade_log"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["orders"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_a"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_b"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["spl_token_prog"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["asc_token_prog"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["system_program"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["system_rent"], is_signer=False, is_writable=False),
    ]
    identifier = b"g\xe2a\xeb\xc8\xbc\xfb\xfe"
    encoded_args = layout.build(
        {
            "inp_agent_nonce": args["inp_agent_nonce"],
            "inp_mkt_vault_nonce": args["inp_mkt_vault_nonce"],
            "inp_prc_vault_nonce": args["inp_prc_vault_nonce"],
            "inp_mkt_decimals": args["inp_mkt_decimals"],
            "inp_prc_decimals": args["inp_prc_decimals"],
            "inp_mkt_mint_type": args["inp_mkt_mint_type"],
            "inp_prc_mint_type": args["inp_prc_mint_type"],
            "inp_manager_actions": args["inp_manager_actions"],
            "inp_expire_enable": args["inp_expire_enable"],
            "inp_expire_min": args["inp_expire_min"],
            "inp_min_quantity": args["inp_min_quantity"],
            "inp_tick_decimals": args["inp_tick_decimals"],
            "inp_taker_fee": args["inp_taker_fee"],
            "inp_maker_rebate": args["inp_maker_rebate"],
            "inp_log_fee": args["inp_log_fee"],
            "inp_log_rebate": args["inp_log_rebate"],
            "inp_log_reimburse": args["inp_log_reimburse"],
            "inp_mkt_vault_uuid": args["inp_mkt_vault_uuid"],
            "inp_prc_vault_uuid": args["inp_prc_vault_uuid"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, PROGRAM_ID, data)
