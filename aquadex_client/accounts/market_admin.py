import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import PROGRAM_ID


class MarketAdminJSON(typing.TypedDict):
    fee_manager: str
    vault_manager: str


@dataclass
class MarketAdmin:
    discriminator: typing.ClassVar = b"n\xab\xeb\xac\x91\xedZ\xbb"
    layout: typing.ClassVar = borsh.CStruct(
        "fee_manager" / BorshPubkey, "vault_manager" / BorshPubkey
    )
    fee_manager: Pubkey
    vault_manager: Pubkey

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["MarketAdmin"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id:
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[Pubkey],
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["MarketAdmin"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["MarketAdmin"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "MarketAdmin":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = MarketAdmin.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            fee_manager=dec.fee_manager,
            vault_manager=dec.vault_manager,
        )

    def to_json(self) -> MarketAdminJSON:
        return {
            "fee_manager": str(self.fee_manager),
            "vault_manager": str(self.vault_manager),
        }

    @classmethod
    def from_json(cls, obj: MarketAdminJSON) -> "MarketAdmin":
        return cls(
            fee_manager=Pubkey.from_string(obj["fee_manager"]),
            vault_manager=Pubkey.from_string(obj["vault_manager"]),
        )
