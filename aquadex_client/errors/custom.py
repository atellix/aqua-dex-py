import typing
from anchorpy.error import ProgramError


class AccessDenied(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "Access denied")

    code = 6000
    name = "AccessDenied"
    msg = "Access denied"


class TokenAccountFrozen(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "Token account frozen")

    code = 6001
    name = "TokenAccountFrozen"
    msg = "Token account frozen"


class InsufficientTokens(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "Insufficient tokens")

    code = 6002
    name = "InsufficientTokens"
    msg = "Insufficient tokens"


class MarketClosed(ProgramError):
    def __init__(self) -> None:
        super().__init__(6003, "Market closed")

    code = 6003
    name = "MarketClosed"
    msg = "Market closed"


class AccountNotFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6004, "Account not found")

    code = 6004
    name = "AccountNotFound"
    msg = "Account not found"


class RecordNotFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6005, "Record not found")

    code = 6005
    name = "RecordNotFound"
    msg = "Record not found"


class OrderNotFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6006, "Order not found")

    code = 6006
    name = "OrderNotFound"
    msg = "Order not found"


class InvalidParameters(ProgramError):
    def __init__(self) -> None:
        super().__init__(6007, "Invalid parameters")

    code = 6007
    name = "InvalidParameters"
    msg = "Invalid parameters"


class InvalidAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6008, "Invalid account")

    code = 6008
    name = "InvalidAccount"
    msg = "Invalid account"


class InvalidDerivedAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6009, "Invalid derived account")

    code = 6009
    name = "InvalidDerivedAccount"
    msg = "Invalid derived account"


class VaultNotEmpty(ProgramError):
    def __init__(self) -> None:
        super().__init__(6010, "Vault not empty")

    code = 6010
    name = "VaultNotEmpty"
    msg = "Vault not empty"


class OrderNotFilled(ProgramError):
    def __init__(self) -> None:
        super().__init__(6011, "Order not filled")

    code = 6011
    name = "OrderNotFilled"
    msg = "Order not filled"


class InternalError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6012, "Internal error")

    code = 6012
    name = "InternalError"
    msg = "Internal error"


class ExternalError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6013, "External error")

    code = 6013
    name = "ExternalError"
    msg = "External error"


class SettlementLogFull(ProgramError):
    def __init__(self) -> None:
        super().__init__(6014, "Settlement log full")

    code = 6014
    name = "SettlementLogFull"
    msg = "Settlement log full"


class SettlementLogNotEmpty(ProgramError):
    def __init__(self) -> None:
        super().__init__(6015, "Settlement log not empty")

    code = 6015
    name = "SettlementLogNotEmpty"
    msg = "Settlement log not empty"


class OrderbookFull(ProgramError):
    def __init__(self) -> None:
        super().__init__(6016, "Orderbook full")

    code = 6016
    name = "OrderbookFull"
    msg = "Orderbook full"


class RetrySettlementAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6017,
            "Settlement log account does not match market, please update market data and retry",
        )

    code = 6017
    name = "RetrySettlementAccount"
    msg = "Settlement log account does not match market, please update market data and retry"


class RebateExceedsFee(ProgramError):
    def __init__(self) -> None:
        super().__init__(6018, "Rebate exceeds fee")

    code = 6018
    name = "RebateExceedsFee"
    msg = "Rebate exceeds fee"


class QuantityBelowMinimum(ProgramError):
    def __init__(self) -> None:
        super().__init__(6019, "Quantity below minimum")

    code = 6019
    name = "QuantityBelowMinimum"
    msg = "Quantity below minimum"


class Overflow(ProgramError):
    def __init__(self) -> None:
        super().__init__(6020, "Overflow")

    code = 6020
    name = "Overflow"
    msg = "Overflow"


CustomError = typing.Union[
    AccessDenied,
    TokenAccountFrozen,
    InsufficientTokens,
    MarketClosed,
    AccountNotFound,
    RecordNotFound,
    OrderNotFound,
    InvalidParameters,
    InvalidAccount,
    InvalidDerivedAccount,
    VaultNotEmpty,
    OrderNotFilled,
    InternalError,
    ExternalError,
    SettlementLogFull,
    SettlementLogNotEmpty,
    OrderbookFull,
    RetrySettlementAccount,
    RebateExceedsFee,
    QuantityBelowMinimum,
    Overflow,
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: AccessDenied(),
    6001: TokenAccountFrozen(),
    6002: InsufficientTokens(),
    6003: MarketClosed(),
    6004: AccountNotFound(),
    6005: RecordNotFound(),
    6006: OrderNotFound(),
    6007: InvalidParameters(),
    6008: InvalidAccount(),
    6009: InvalidDerivedAccount(),
    6010: VaultNotEmpty(),
    6011: OrderNotFilled(),
    6012: InternalError(),
    6013: ExternalError(),
    6014: SettlementLogFull(),
    6015: SettlementLogNotEmpty(),
    6016: OrderbookFull(),
    6017: RetrySettlementAccount(),
    6018: RebateExceedsFee(),
    6019: QuantityBelowMinimum(),
    6020: Overflow(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
