from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class ManagerTransferSolArgs(typing.TypedDict):
    inp_withdraw: bool
    inp_all: bool
    inp_amount: int


layout = borsh.CStruct(
    "inp_withdraw" / borsh.Bool, "inp_all" / borsh.Bool, "inp_amount" / borsh.U64
)


class ManagerTransferSolAccounts(typing.TypedDict):
    market: Pubkey
    state: Pubkey
    admin: Pubkey
    manager: Pubkey


def manager_transfer_sol(
    args: ManagerTransferSolArgs,
    accounts: ManagerTransferSolAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["admin"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["manager"], is_signer=True, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"^\xab\x02\xe4\xfb\xda!X"
    encoded_args = layout.build(
        {
            "inp_withdraw": args["inp_withdraw"],
            "inp_all": args["inp_all"],
            "inp_amount": args["inp_amount"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
